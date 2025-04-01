import os
import sys
import logging
from datetime import datetime

def setup_logging(config=None):
    """
    Set up logging configuration based on environment variables or config dict
    
    Args:
        config: Optional dictionary with logging configuration
    """
    if config is None:
        config = {}
    
    # Get logging settings from config or environment variables
    log_level_name = config.get('level') or os.getenv('LOG_LEVEL', 'INFO')
    log_file = config.get('file') or os.getenv('LOG_FILE', 'people_agent.log')
    log_format = config.get('format') or os.getenv('LOG_FORMAT', 
                                                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Convert log level string to actual level
    log_level = getattr(logging, log_level_name.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers to avoid duplicate logs
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # Add file handler
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up log file: {e}")
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Return configured logger
    return root_logger