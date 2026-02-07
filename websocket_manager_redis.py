"""
Redis-Enhanced WebSocket Manager for Multi-Instance Real-Time Updates

Supports both single-instance (in-memory) and multi-instance (Redis pub/sub) modes.
Automatically detects Redis availability and switches modes accordingly.
"""
import os
import json
import asyncio
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Try to import Redis (optional dependency)
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️  redis package not installed. Running in single-instance mode.")


class RedisConnectionManager:
    """
    Enhanced WebSocket connection manager with Redis pub/sub support.

    Features:
    - Multi-instance broadcasting via Redis pub/sub
    - Automatic fallback to in-memory mode if Redis unavailable
    - User-specific and global broadcasting
    - Automatic connection cleanup
    - Health monitoring
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the connection manager.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379)
                      If None, will check REDIS_URL environment variable
        """
        # Local connection storage (always maintained)
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.all_connections: Set[WebSocket] = set()

        # Redis configuration
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_enabled = bool(self.redis_url and REDIS_AVAILABLE)

        # Redis clients (initialized in startup)
        self.redis_client: Optional[aioredis.Redis] = None
        self.redis_pubsub = None
        self._pubsub_task = None

        # Channels for pub/sub
        self.BROADCAST_CHANNEL = "websocket:broadcast:all"
        self.USER_CHANNEL_PREFIX = "websocket:broadcast:user:"

        if self.redis_enabled:
            logger.info(f"✅ Redis WebSocket manager enabled: {self.redis_url}")
        else:
            logger.info("ℹ️  Redis disabled. Running in single-instance mode.")

    async def startup(self):
        """Initialize Redis connections (call this on app startup)"""
        if not self.redis_enabled:
            return

        try:
            # Create Redis client
            self.redis_client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=10
            )

            # Test connection
            await self.redis_client.ping()

            # Initialize pub/sub
            self.redis_pubsub = self.redis_client.pubsub()

            # Subscribe to broadcast channel
            await self.redis_pubsub.subscribe(self.BROADCAST_CHANNEL)

            # Start listening task
            self._pubsub_task = asyncio.create_task(self._redis_listener())

            logger.info("✅ Redis pub/sub initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Redis: {e}")
            logger.warning("⚠️  Falling back to single-instance mode")
            self.redis_enabled = False
            self.redis_client = None

    async def shutdown(self):
        """Cleanup Redis connections (call this on app shutdown)"""
        if self._pubsub_task:
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass

        if self.redis_pubsub:
            await self.redis_pubsub.unsubscribe(self.BROADCAST_CHANNEL)
            await self.redis_pubsub.close()

        if self.redis_client:
            await self.redis_client.close()

        logger.info("✅ Redis connections closed")

    async def _redis_listener(self):
        """Background task to listen for Redis pub/sub messages"""
        try:
            while True:
                message = await self.redis_pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )

                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        channel = message['channel']

                        # Handle broadcast to all
                        if channel == self.BROADCAST_CHANNEL:
                            await self._local_broadcast_to_all(data)

                        # Handle user-specific broadcast
                        elif channel.startswith(self.USER_CHANNEL_PREFIX):
                            user_id = int(channel.split(':')[-1])
                            await self._local_broadcast_to_user(user_id, data)

                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")

                await asyncio.sleep(0.01)  # Prevent tight loop

        except asyncio.CancelledError:
            logger.info("Redis listener task cancelled")
        except Exception as e:
            logger.error(f"Redis listener error: {e}")

    async def connect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection
            user_id: Optional user ID for user-specific broadcasts
        """
        await websocket.accept()
        self.all_connections.add(websocket)

        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)

            # Subscribe to user-specific channel in Redis
            if self.redis_enabled and self.redis_pubsub:
                user_channel = f"{self.USER_CHANNEL_PREFIX}{user_id}"
                await self.redis_pubsub.subscribe(user_channel)

            logger.info(f"✅ WebSocket connected for user {user_id} (Total: {len(self.all_connections)})")
        else:
            logger.info(f"✅ WebSocket connected (anonymous) (Total: {len(self.all_connections)})")

    def disconnect(self, websocket: WebSocket, user_id: Optional[int] = None):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
            user_id: Optional user ID
        """
        self.all_connections.discard(websocket)

        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                # Note: We don't unsubscribe from Redis here because other instances
                # might still have connections for this user
            logger.info(f"❌ WebSocket disconnected for user {user_id} (Total: {len(self.all_connections)})")
        else:
            logger.info(f"❌ WebSocket disconnected (anonymous) (Total: {len(self.all_connections)})")

    async def _local_broadcast_to_user(self, user_id: int, message: dict):
        """
        Broadcast to local connections for a specific user (called from Redis listener).

        Args:
            user_id: The user ID to broadcast to
            message: The message dictionary to send
        """
        if user_id not in self.active_connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_str)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, user_id)

    async def _local_broadcast_to_all(self, message: dict):
        """
        Broadcast to all local connections (called from Redis listener).

        Args:
            message: The message dictionary to send
        """
        if not self.all_connections:
            return

        message_str = json.dumps(message)
        disconnected = set()

        for connection in self.all_connections:
            try:
                await connection.send_text(message_str)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to all: {e}")
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            # Find and remove from user-specific connections
            for user_id, connections in list(self.active_connections.items()):
                if connection in connections:
                    self.disconnect(connection, user_id)
                    break
            else:
                self.all_connections.discard(connection)

    async def broadcast_to_user(self, user_id: int, message: dict):
        """
        Broadcast a message to all connections for a specific user across all instances.

        Args:
            user_id: The user ID to broadcast to
            message: The message dictionary to send
        """
        if self.redis_enabled and self.redis_client:
            # Publish to Redis - will be received by all instances
            try:
                user_channel = f"{self.USER_CHANNEL_PREFIX}{user_id}"
                await self.redis_client.publish(
                    user_channel,
                    json.dumps(message)
                )
                logger.debug(f"📤 Published to Redis channel: {user_channel}")
            except Exception as e:
                logger.error(f"Redis publish error: {e}")
                # Fallback to local broadcast
                await self._local_broadcast_to_user(user_id, message)
        else:
            # Single instance mode - broadcast locally
            await self._local_broadcast_to_user(user_id, message)

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all connected clients across all instances.

        Args:
            message: The message dictionary to send
        """
        if self.redis_enabled and self.redis_client:
            # Publish to Redis - will be received by all instances
            try:
                await self.redis_client.publish(
                    self.BROADCAST_CHANNEL,
                    json.dumps(message)
                )
                logger.debug(f"📤 Published to Redis channel: {self.BROADCAST_CHANNEL}")
            except Exception as e:
                logger.error(f"Redis publish error: {e}")
                # Fallback to local broadcast
                await self._local_broadcast_to_all(message)
        else:
            # Single instance mode - broadcast locally
            await self._local_broadcast_to_all(message)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    def get_connection_count(self) -> int:
        """Get the total number of active connections on this instance"""
        return len(self.all_connections)

    def get_user_connection_count(self, user_id: int) -> int:
        """Get the number of active connections for a specific user on this instance"""
        return len(self.active_connections.get(user_id, set()))

    async def get_global_stats(self) -> dict:
        """
        Get global connection statistics across all instances (if Redis enabled).

        Returns:
            dict: Statistics including total connections, users, instances
        """
        stats = {
            "local_connections": len(self.all_connections),
            "local_users": len(self.active_connections),
            "redis_enabled": self.redis_enabled,
        }

        if self.redis_enabled and self.redis_client:
            try:
                # Store instance stats in Redis with TTL
                instance_key = f"websocket:instance:{id(self)}"
                await self.redis_client.setex(
                    instance_key,
                    30,  # 30 second TTL
                    json.dumps(stats)
                )

                # Count active instances
                instance_keys = await self.redis_client.keys("websocket:instance:*")
                stats["total_instances"] = len(instance_keys)

                # Aggregate stats from all instances
                total_connections = 0
                for key in instance_keys:
                    data = await self.redis_client.get(key)
                    if data:
                        instance_data = json.loads(data)
                        total_connections += instance_data.get("local_connections", 0)

                stats["total_connections"] = total_connections

            except Exception as e:
                logger.error(f"Error getting global stats: {e}")

        return stats


# Create global manager instance
# Will auto-detect Redis from REDIS_URL environment variable
manager = RedisConnectionManager()
