"""
WebSocket Manager for Real-Time Updates
Manages WebSocket connections and broadcasts task updates to connected clients
"""
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.
    Supports user-specific rooms for targeted broadcasting.
    """

    def __init__(self):
        # Store active connections: {user_id: set of WebSocket connections}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Store all connections (for broadcast to all)
        self.all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int = None):
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
            logger.info(f"✅ WebSocket connected for user {user_id}")
        else:
            logger.info("✅ WebSocket connected (anonymous)")

    def disconnect(self, websocket: WebSocket, user_id: int = None):
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
            logger.info(f"❌ WebSocket disconnected for user {user_id}")
        else:
            logger.info("❌ WebSocket disconnected (anonymous)")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_user(self, user_id: int, message: dict):
        """
        Broadcast a message to all connections for a specific user.

        Args:
            user_id: The user ID to broadcast to
            message: The message dictionary to send
        """
        if user_id not in self.active_connections:
            logger.debug(f"No active connections for user {user_id}")
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

        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected WebSocket(s) for user {user_id}")

    async def broadcast_to_all(self, message: dict):
        """
        Broadcast a message to all connected clients.

        Args:
            message: The message dictionary to send
        """
        if not self.all_connections:
            logger.debug("No active connections to broadcast to")
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
                # Not in any user-specific set, just remove from all_connections
                self.all_connections.discard(connection)

        if disconnected:
            logger.info(f"Cleaned up {len(disconnected)} disconnected WebSocket(s)")

    def get_connection_count(self) -> int:
        """Get the total number of active connections"""
        return len(self.all_connections)

    def get_user_connection_count(self, user_id: int) -> int:
        """Get the number of active connections for a specific user"""
        return len(self.active_connections.get(user_id, set()))


# Global connection manager instance
manager = ConnectionManager()
