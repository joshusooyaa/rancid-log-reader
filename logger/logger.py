import structlog
import sys
import time
import os
from datetime import datetime
from typing import Any, Dict

def reorder_fields(logger, method_name, event_dict):
    """Reorder fields to ensure timestamp and level are first."""
    ordered_dict = {}
    # First add timestamp and level
    if "timestamp" in event_dict:
        ordered_dict["timestamp"] = event_dict.pop("timestamp")
    if "level" in event_dict:
        ordered_dict["level"] = event_dict.pop("level")
    if "event" in event_dict:
        ordered_dict["event"] = event_dict.pop("event")
    # Add stack info if present
    if "stack_info" in event_dict:
        ordered_dict["stack_info"] = event_dict.pop("stack_info")
    # Add all remaining fields
    ordered_dict.update(event_dict)
    return ordered_dict

def add_stack_info(logger, method_name, event_dict):
    """Add stack info to the log record."""
    import traceback
    frames = traceback.extract_stack()
    # Filter frames to only include our app code
    app_frames = [
        frame for frame in frames[:-3]  # Skip the last 3 frames (logging machinery)
        if "site-packages" not in frame.filename  # Skip library code
    ]
    if app_frames:
        event_dict["stack_info"] = "".join(traceback.format_list(app_frames))
    return event_dict

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create logger instance
logger = structlog.get_logger()

def get_logger():
    """
    Returns a configured structlog logger instance.
    
    Usage:
        logger = get_logger()
        logger.info("message", custom_field="value")
        logger.warning("warning message", extra_data=123)
        logger.error("error message", error_code=500)
    """
    return logger

# Convenience methods for common log levels
def info(msg, **kwargs):
    """Log an info message with optional additional fields."""
    logger.info(msg, **kwargs)

def warning(msg, **kwargs):
    """Log a warning message with optional additional fields."""
    logger.warning(msg, **kwargs)

def error(msg, **kwargs):
    """Log an error message with optional additional fields."""
    logger.error(msg, **kwargs)
