"""
WebSocket Router for Real-Time Updates
Provides WebSocket endpoints for frontend clients to receive real-time task updates
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional

from websocket_manager import manager
from auth_utils import get_current_user_ws
from models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/tasks")
async def websocket_tasks_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time task updates.

    Frontend connects to: ws://localhost:8000/ws/tasks?token=<jwt_token>

    Messages sent to client:
    - task_created: When a new task is created
    - task_completed: When a task is completed
    - task_updated: When a task is updated (future)
    - task_deleted: When a task is deleted (future)

    Message format:
    {
        "type": "task_created" | "task_completed" | "task_updated" | "task_deleted",
        "data": {
            "id": 1,
            "title": "Task title",
            "description": "Task description",
            ...
        }
    }
    """
    user_id = None

    # Authenticate user from token
    if token:
        try:
            from auth_utils import decode_access_token
            payload = decode_access_token(token)
            user_id = payload.get("user_id")
            logger.info(f"WebSocket authenticated for user {user_id}")
        except Exception as e:
            logger.warning(f"WebSocket authentication failed: {e}")
            await websocket.close(code=1008, reason="Authentication failed")
            return
    else:
        logger.info("WebSocket connection without authentication")

    # Connect the WebSocket
    await manager.connect(websocket, user_id)

    try:
        # Send initial connection confirmation
        await manager.send_personal_message(
            '{"type": "connected", "message": "WebSocket connected successfully"}',
            websocket
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (ping/pong, subscriptions, etc.)
                data = await websocket.receive_text()
                logger.debug(f"Received WebSocket message: {data}")

                # Handle ping/pong for keepalive
                if data == "ping":
                    await manager.send_personal_message('{"type": "pong"}', websocket)

            except WebSocketDisconnect:
                logger.info("WebSocket disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error in WebSocket receive loop: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Disconnect the WebSocket
        manager.disconnect(websocket, user_id)


@router.get("/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics.
    Useful for monitoring and debugging.
    """
    return {
        "total_connections": manager.get_connection_count(),
        "user_connections": len(manager.active_connections),
    }
