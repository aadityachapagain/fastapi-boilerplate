import logging
from pyee import EventEmitter
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

# global event emitter
emitter = EventEmitter()


def init_event_listeners():
    """Initialize all event listeners."""
    logger.info("Initializing event listeners")
    # must be called at app startup to register all event listeners
    # Listeners should be imported and registered here


def emit_event(event_name: str, data: Dict[str, Any]):
    """Emit an event with data.
    
    Args:
        event_name: The name of the event
        data: Data to be passed to event listeners
    """
    logger.debug(f"Emitting event: {event_name} with data: {data}")
    emitter.emit(event_name, data)


def register_listener(event_name: str, listener: Callable):
    """Register a listener for an event.
    
    Args:
        event_name: The name of the event to listen for
        listener: The function to call when the event is emitted
    """
    logger.debug(f"Registering listener for event: {event_name}")
    emitter.on(event_name, listener)


def remove_listener(event_name: str, listener: Callable):
    """Remove a listener for an event.
    
    Args:
        event_name: The name of the event
        listener: The function to remove
    """
    logger.debug(f"Removing listener for event: {event_name}")
    emitter.remove_listener(event_name, listener)