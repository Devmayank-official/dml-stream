"""
Logging utilities for YouTube Downloader.

This module provides logging configuration and helpers for
consistent logging across the application.
"""

import functools
import json
import logging
import logging.handlers
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from dml_stream.core.constants import (
    CONSOLE_LOG_FORMAT,
    LOG_DATE_FORMAT,
)


class JSONFormatter(logging.Formatter):
    """
    Custom formatter to output logs in JSON format.
    
    Useful for structured logging and log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        for key, value in record.__dict__.items():
            if key not in ('name', 'msg', 'args', 'created', 'filename', 'funcName',
                          'levelname', 'levelno', 'lineno', 'module', 'msecs',
                          'pathname', 'process', 'processName', 'relativeCreated',
                          'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                          'message', 'asctime'):
                try:
                    json.dumps(value)  # Check if JSON serializable
                    log_entry[key] = value
                except (TypeError, ValueError):
                    log_entry[key] = str(value)

        return json.dumps(log_entry)


class ColoredConsoleHandler(logging.StreamHandler):
    """
    Console handler with colored output for different log levels.
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record with color."""
        try:
            color = self.COLORS.get(record.levelname, self.RESET)

            if self.stream and hasattr(self.stream, 'isatty') and self.stream.isatty():
                record.levelname = f"{color}{record.levelname}{self.RESET}"

            super().emit(record)
        except Exception:
            self.handleError(record)


def setup_logging(
    log_file: Optional[str] = None,
    log_level: str = "INFO",
    console_output: bool = True,
    json_format: bool = False,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        log_file: Path to log file (None for no file logging).
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        console_output: Enable console output.
        json_format: Use JSON format for file logs.
        max_bytes: Maximum log file size before rotation.
        backup_count: Number of backup log files to keep.
        
    Returns:
        Root logger for the application.
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    if console_output:
        console_handler = ColoredConsoleHandler()
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_formatter = logging.Formatter(CONSOLE_LOG_FORMAT, LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        try:
            # Ensure log directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            if json_format:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler = logging.handlers.RotatingFileHandler(
                    log_file,
                    maxBytes=max_bytes,
                    backupCount=backup_count,
                    encoding='utf-8'
                )
                file_formatter = logging.Formatter(CONSOLE_LOG_FORMAT, LOG_DATE_FORMAT)
                file_handler.setFormatter(file_formatter)

            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            logger.addHandler(file_handler)

        except Exception as e:
            logger.warning(f"Failed to set up log file '{log_file}': {str(e)}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__).
        
    Returns:
        Logger instance.
    """
    return logging.getLogger(name)


def log_function_call(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG,
    log_args: bool = False,
    log_result: bool = False
) -> Callable:
    """
    Decorator to log function calls.
    
    Args:
        logger: Logger to use (uses function's module logger if None).
        level: Log level for messages.
        log_args: Whether to log function arguments.
        log_result: Whether to log function result.
        
    Returns:
        Decorated function.
        
    Example:
        @log_function_call(log_args=True, log_result=True)
        def my_function(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get logger
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            # Log function call
            func_name = f"{func.__module__}.{func.__name__}"

            if log_args:
                args_str = ", ".join(
                    [repr(a) for a in args] +
                    [f"{k}={v!r}" for k, v in kwargs.items()]
                )
                logger.log(level, f"Calling {func_name}({args_str})")
            else:
                logger.log(level, f"Calling {func_name}")

            # Execute function and measure time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time

                if log_result:
                    logger.log(level, f"{func_name} returned: {result!r} ({elapsed:.3f}s)")
                else:
                    logger.log(level, f"{func_name} completed ({elapsed:.3f}s)")

                return result

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{func_name} raised {type(e).__name__}: {str(e)} ({elapsed:.3f}s)")
                raise

        return wrapper
    return decorator


class LogContext:
    """
    Context manager for adding contextual information to logs.
    
    Example:
        with LogContext(logger, user_id=123, action="download"):
            perform_download()
    """

    def __init__(self, logger: logging.Logger, **context: Any) -> None:
        """
        Initialize log context.
        
        Args:
            logger: Logger to add context to.
            **context: Contextual key-value pairs.
        """
        self.logger = logger
        self.context = context
        self.old_factory = None

    def __enter__(self) -> 'LogContext':
        """Add context to logger."""
        self.old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Remove context from logger."""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


class PerformanceLogger:
    """
    Context manager for logging performance of code blocks.
    
    Example:
        with PerformanceLogger(logger, "Database query"):
            result = db.query()
    """

    def __init__(
        self,
        logger: logging.Logger,
        operation: str,
        level: int = logging.DEBUG,
        threshold: Optional[float] = None
    ) -> None:
        """
        Initialize performance logger.
        
        Args:
            logger: Logger to use.
            operation: Operation name for logging.
            level: Log level.
            threshold: Log warning if operation takes longer than this (seconds).
        """
        self.logger = logger
        self.operation = operation
        self.level = level
        self.threshold = threshold
        self.start_time: Optional[float] = None

    def __enter__(self) -> 'PerformanceLogger':
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Log performance."""
        if self.start_time is None:
            return

        elapsed = time.time() - self.start_time

        if exc_type:
            self.logger.error(f"{self.operation} failed after {elapsed:.3f}s")
        elif self.threshold and elapsed > self.threshold:
            self.logger.warning(
                f"{self.operation} took {elapsed:.3f}s (threshold: {self.threshold}s)"
            )
        else:
            self.logger.log(self.level, f"{self.operation} completed in {elapsed:.3f}s")


def log_execution_time(
    logger: Optional[logging.Logger] = None,
    level: int = logging.DEBUG
) -> Callable:
    """
    Decorator to log function execution time.
    
    Args:
        logger: Logger to use.
        level: Log level.
        
    Returns:
        Decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            start = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start
                logger.log(level, f"{func.__name__} executed in {elapsed:.3f}s")
                return result
            except Exception:
                elapsed = time.time() - start
                logger.error(f"{func.__name__} failed after {elapsed:.3f}s")
                raise
        return wrapper
    return decorator
