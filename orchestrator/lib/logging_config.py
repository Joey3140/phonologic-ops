"""
Structured logging configuration for the orchestrator.

Replaces print statements with proper logging that can be:
- Filtered by level (DEBUG, INFO, WARNING, ERROR)
- Sent to external services (DataDog, Sentry)
- Traced across requests
"""
import logging
import sys
from datetime import datetime, timezone
from typing import Optional
import json


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging - ideal for log aggregation services."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry)


class OrchestratorLogger:
    """
    Centralized logger for the orchestrator.
    
    Usage:
        from lib.logging_config import logger
        logger.info("Processing contribution", contribution_id="abc123")
        logger.error("Redis failed", error=str(e), operation="save_pending")
    """
    
    def __init__(self, name: str = "orchestrator"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if not self._logger.handlers:
            # Console handler with human-readable format for dev
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_format = logging.Formatter(
                "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            console_handler.setFormatter(console_format)
            self._logger.addHandler(console_handler)
    
    def _log(self, level: int, message: str, **kwargs):
        """Log with extra context fields."""
        extra = {"extra_fields": kwargs} if kwargs else {}
        self._logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


# Singleton logger instance
logger = OrchestratorLogger()
