"""
Logging Configuration for Almanac Futures

Provides centralized logging configuration for the entire application.
"""

import logging
import logging.handlers
import os
from datetime import datetime
import sys


def setup_logging(log_level=logging.INFO, log_file=None):
    """
    Set up logging configuration for the application.
    
    Args:
        log_level (int): Logging level (default: INFO)
        log_file (str): Optional log file path
    """
    # Create logs directory if it doesn't exist
    if log_file and not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('dash').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name):
    """
    Get a logger instance for a specific module.
    
    Args:
        name (str): Logger name (usually __name__)
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class LoggingMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    @property
    def logger(self):
        """Get logger for this class."""
        return logging.getLogger(self.__class__.__name__)
    
    def log_info(self, message, *args, **kwargs):
        """Log info message."""
        self.logger.info(message, *args, **kwargs)
    
    def log_warning(self, message, *args, **kwargs):
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)
    
    def log_error(self, message, *args, **kwargs):
        """Log error message."""
        self.logger.error(message, *args, **kwargs)
    
    def log_debug(self, message, *args, **kwargs):
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)
