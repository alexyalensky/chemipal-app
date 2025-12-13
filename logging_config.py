"""
Centralized logging configuration for ChemiPal Integration System.

This module provides a unified logging setup for the entire application.
All modules should use get_logger(__name__) instead of basicConfig.
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Track if logging has been initialized
_logging_initialized = False


def setup_logging():
    """
    Initialize unified logging configuration for entire application.
    Safe to call multiple times - only initializes once.
    
    Configuration:
    - File (app.log): DEBUG and above, 50MB rotation
    - File (errors.log): ERROR and above, 10MB rotation
    - Suppresses noisy third-party logs
    - No console output (designed for service operation)
    """
    global _logging_initialized
    
    # If already initialized, do nothing
    if _logging_initialized:
        return
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove all existing handlers to prevent duplicates
    logger.handlers.clear()
    
    # Create log directory if it doesn't exist
    os.makedirs('log', exist_ok=True)
    
    # Configure formatter - consistent format across all logs
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Rotating file handler for all logs (UTF-8 encoding for Hebrew characters)
    file_handler = RotatingFileHandler(
        'log/app.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Separate file for errors only (UTF-8 encoding for Hebrew characters)
    error_handler = RotatingFileHandler(
        'log/errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers (no console handler - logs only to files for service operation)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Disable logging exceptions to prevent encoding errors from crashing
    # This ensures Hebrew characters are written to UTF-8 files without console errors
    logging.raiseExceptions = False
    
    # Suppress noisy third-party logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    
    # Mark as initialized
    _logging_initialized = True
    
    return logger


def get_logger(name: str):
    """
    Get a logger instance for a module/class.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

