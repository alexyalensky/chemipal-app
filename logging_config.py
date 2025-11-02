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
    - Console: INFO and above
    - File (app.log): DEBUG and above, 50MB rotation
    - File (errors.log): ERROR and above, 10MB rotation
    - Suppresses noisy third-party logs
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
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(detailed_formatter)
    
    # Rotating file handler for all logs
    file_handler = RotatingFileHandler(
        'log/app.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Separate file for errors only
    error_handler = RotatingFileHandler(
        'log/errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Suppress noisy third-party logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    
    # Legacy log file for backward compatibility
    legacy_handler = RotatingFileHandler(
        'log/log.txt',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    legacy_handler.setLevel(logging.DEBUG)
    # Use simpler format for legacy compatibility
    legacy_formatter = logging.Formatter(
        '%(levelname)s:%(name)s:%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    legacy_handler.setFormatter(legacy_formatter)
    logger.addHandler(legacy_handler)
    
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

