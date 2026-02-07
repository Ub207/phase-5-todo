"""
Kafka Consumer Service - Runs as a background task in FastAPI
Consumes events from Kafka and updates the database in real-time
"""
import asyncio
import json
import logging
from typing import Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from database import SessionLocal
from models import Task, User
from events import publish_event  # For broadcasting to WebSocket clients

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    """
    Kafka consumer service that runs as a background task in FastAPI.
    Consumes events from Kafka topics and updates the database.
    """

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.running = False

    def create_consumer(self):
        """Create and configure the Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                'task-events',  # Primary topic
                bootstrap_servers=[self.bootstrap_servers],
                auto_offset_reset='latest',  # Only consume new messages
                enable_auto_commit=True,
                group_id='fastapi-backend-consumer',
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                consumer_timeout_ms=1000  # Timeout to allow graceful shutdown
            )
            logger.info(f"✅ Kafka consumer created successfully: {self.bootstrap_servers}")
            return True
        except KafkaError as e:
            logger.error(f"❌ Failed to create Kafka consumer: {e}")
            return False

    def handle_task_created(self, db: Session, event_data: Dict[str, Any]) -> None:
        """
        Handle task_created event by inserting a new task into the database.

        Args:
            db: SQLAlchemy database session
            event_data: Event payload containing task details
        """
        try:
            task_id = event_data.get('id')
            title = event_data.get('title')
            user_id = event_data.get('user_id')
            description = event_data.get('description', '')
            priority = event_data.get('priority', 'medium')
            due_date_str = event_data.get('due_date')

            # Validate required fields
            if not all([task_id, title, user_id]):
                logger.error(f"Missing required fields in task_created event: {event_data}")
                return

            # Check if task already exists (idempotency)
            existing_task = db.query(Task).filter(Task.id == task_id).first()
            if existing_task:
                logger.info(f"Task {task_id} already exists. Skipping creation.")
                return

            # Parse due_date if provided
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                except (ValueError, AttributeError):
                    logger.warning(f"Invalid due_date format: {due_date_str}")

            # Create new task
            new_task = Task(
                id=task_id,
                title=title,
                description=description,
                user_id=user_id,
                priority=priority,
                due_date=due_date,
                completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(new_task)
            db.commit()
            db.refresh(new_task)

            logger.info(f"✅ Task created from Kafka: task_id={task_id}, title='{title}'")

            # Broadcast to WebSocket clients for real-time updates
            publish_event("task_created_realtime", {
                "id": new_task.id,
                "title": new_task.title,
                "description": new_task.description,
                "user_id": new_task.user_id,
                "priority": new_task.priority,
                "completed": new_task.completed,
            })

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while creating task: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while creating task: {e}")

    def handle_task_completed(self, db: Session, event_data: Dict[str, Any]) -> None:
        """
        Handle task_completed event by marking a task as completed in the database.

        Args:
            db: SQLAlchemy database session
            event_data: Event payload containing task_id
        """
        try:
            task_id = event_data.get('id')

            if not task_id:
                logger.error(f"Missing task_id in task_completed event: {event_data}")
                return

            # Find and update the task
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                logger.warning(f"Task not found for task_id={task_id}")
                return

            # Only update if not already completed (idempotency)
            if task.completed:
                logger.info(f"Task {task_id} already marked as completed. Skipping.")
                return

            task.completed = True
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()

            db.commit()
            db.refresh(task)

            logger.info(f"✅ Task marked as completed from Kafka: task_id={task_id}")

            # Broadcast to WebSocket clients for real-time updates
            publish_event("task_completed_realtime", {
                "id": task.id,
                "title": task.title,
                "completed": task.completed,
                "completed_at": str(task.completed_at),
            })

        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error while completing task: {e}")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error while completing task: {e}")

    def process_event(self, message: Dict[str, Any]) -> None:
        """
        Process incoming Kafka event and route to appropriate handler.

        Args:
            message: Deserialized Kafka message
        """
        event_type = message.get('event_type') or message.get('type')

        if not event_type:
            logger.warning(f"Event missing 'event_type' or 'type' field: {message}")
            return

        logger.info(f"📩 Processing Kafka event: {event_type}")

        # Create database session for this event
        db = SessionLocal()
        try:
            # Route event to appropriate handler
            if event_type == 'task_created':
                # Use 'data' field if present, otherwise use message directly
                event_data = message.get('data', message)
                self.handle_task_created(db, event_data)
            elif event_type == 'task_completed':
                event_data = message.get('data', message)
                self.handle_task_completed(db, event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")
        finally:
            db.close()

    async def start(self):
        """Start the Kafka consumer in the background"""
        if not self.create_consumer():
            logger.error("Failed to create Kafka consumer. Service will not start.")
            return

        self.running = True
        logger.info("🚀 Kafka consumer service started. Listening for events...")

        try:
            # Run consumer in event loop
            while self.running:
                try:
                    # Poll for messages with timeout
                    message_batch = self.consumer.poll(timeout_ms=1000)

                    for topic_partition, messages in message_batch.items():
                        for message in messages:
                            try:
                                self.process_event(message.value)
                            except Exception as e:
                                logger.error(f"Error processing message: {e}", exc_info=True)

                    # Allow other async tasks to run
                    await asyncio.sleep(0.1)

                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}", exc_info=True)
                    await asyncio.sleep(1)  # Wait before retrying

        except asyncio.CancelledError:
            logger.info("Kafka consumer task cancelled")
        finally:
            self.stop()

    def stop(self):
        """Stop the Kafka consumer gracefully"""
        self.running = False
        if self.consumer:
            try:
                self.consumer.close()
                logger.info("✅ Kafka consumer closed successfully")
            except Exception as e:
                logger.error(f"Error closing Kafka consumer: {e}")


# Global instance
kafka_service = KafkaConsumerService()
