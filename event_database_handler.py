"""
Event Database Handler - Kafka Consumer for Task Events
Consumes task events from Kafka and updates the SQLite database
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./todo.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Models (mirroring the existing schema)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String, default="medium")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RecurringRule(Base):
    __tablename__ = "recurring_rules"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    frequency = Column(String, nullable=False)
    interval = Column(Integer, default=1)
    next_occurrence = Column(DateTime, nullable=False)


def handle_task_created(db_session, event_data: Dict[str, Any]) -> None:
    """
    Handle task_created event by inserting a new task into the database.

    Args:
        db_session: SQLAlchemy database session
        event_data: Event payload containing task details
    """
    try:
        # Extract task details from event
        task_id = event_data.get('task_id')
        title = event_data.get('title')
        user_id = event_data.get('user_id')
        description = event_data.get('description', '')
        priority = event_data.get('priority', 'medium')

        # Validate required fields
        if not all([task_id, title, user_id]):
            logger.error(f"Missing required fields in task_created event: {event_data}")
            return

        # Create new task
        new_task = Task(
            id=task_id,
            title=title,
            description=description,
            user_id=user_id,
            priority=priority,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db_session.add(new_task)
        db_session.commit()

        logger.info(f"Task created successfully: task_id={task_id}, title='{title}', user_id={user_id}")

    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Database error while creating task: {e}")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Unexpected error while creating task: {e}")


def handle_task_completed(db_session, event_data: Dict[str, Any]) -> None:
    """
    Handle task_completed event by marking a task as completed in the database.

    Args:
        db_session: SQLAlchemy database session
        event_data: Event payload containing task_id
    """
    try:
        # Extract task_id from event
        task_id = event_data.get('task_id')

        if not task_id:
            logger.error(f"Missing task_id in task_completed event: {event_data}")
            return

        # Find and update the task
        task = db_session.query(Task).filter(Task.id == task_id).first()

        if not task:
            logger.warning(f"Task not found for task_id={task_id}")
            return

        task.completed = True
        task.updated_at = datetime.utcnow()

        db_session.commit()

        logger.info(f"Task marked as completed: task_id={task_id}, title='{task.title}'")

    except SQLAlchemyError as e:
        db_session.rollback()
        logger.error(f"Database error while completing task: {e}")
    except Exception as e:
        db_session.rollback()
        logger.error(f"Unexpected error while completing task: {e}")


def process_event(db_session, message: Dict[str, Any]) -> None:
    """
    Process incoming Kafka event and route to appropriate handler.

    Args:
        db_session: SQLAlchemy database session
        message: Deserialized Kafka message
    """
    event_type = message.get('event_type')
    event_data = message.get('data', {})

    logger.info(f"Processing event: {event_type}")

    # Route event to appropriate handler
    if event_type == 'task_created':
        handle_task_created(db_session, event_data)
    elif event_type == 'task_completed':
        handle_task_completed(db_session, event_data)
    else:
        logger.warning(f"Unknown event type: {event_type}")


def main():
    """
    Main function to consume Kafka messages and process task events.
    """
    # Initialize Kafka consumer
    consumer = KafkaConsumer(
        'task-events',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='event-database-handler',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    logger.info("Kafka consumer started. Listening for task events on 'task-events' topic...")

    try:
        # Consume messages from Kafka
        for message in consumer:
            try:
                # Create database session for each message
                db_session = SessionLocal()

                try:
                    # Process the event
                    process_event(db_session, message.value)
                finally:
                    # Always close the session
                    db_session.close()

            except json.JSONDecodeError as e:
                logger.error(f"Failed to deserialize message: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user. Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error in consumer: {e}")
    finally:
        # Close the consumer
        consumer.close()
        logger.info("Kafka consumer closed.")


if __name__ == "__main__":
    main()
