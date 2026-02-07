"""
Lightweight in-memory event system.
Designed to be easily replaceable by Kafka/Dapr later.
"""
import logging
from typing import Callable, Dict, List, Any
from threading import Lock

logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-memory event bus with thread-safe listener management."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._lock = Lock()

    def subscribe(self, event_type: str, handler: Callable):
        """Register a handler for an event type."""
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(handler)
            logger.info(f"Subscribed handler {handler.__name__} to event '{event_type}'")

    def publish(self, event_type: str, data: Any):
        """Publish an event to all registered handlers."""
        with self._lock:
            handlers = self._listeners.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers for event '{event_type}'")
            return

        logger.info(f"Publishing event '{event_type}' to {len(handlers)} handler(s)")

        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Error in handler {handler.__name__} for event '{event_type}': {e}")

    def clear(self):
        """Clear all listeners (useful for testing)."""
        with self._lock:
            self._listeners.clear()


# Global event bus instance
event_bus = EventBus()


def publish_event(event_type: str, data: Any):
    """Convenience function to publish events."""
    event_bus.publish(event_type, data)


def subscribe_to_event(event_type: str):
    """Decorator to register event handlers."""
    def decorator(func: Callable):
        event_bus.subscribe(event_type, func)
        return func
    return decorator
