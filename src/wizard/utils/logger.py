"""
Logging configuration for CAPES Research Wizard.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(level="INFO"):
    """
    Configure the application-wide logging system.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Convert string level to logging level constant
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Create log file handler
    log_dir = get_log_directory()
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "wizard.log"), maxBytes=5 * 1024 * 1024, backupCount=3  # 5 MB
    )
    file_handler.setLevel(numeric_level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Set formatters
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Log setup completion
    logger.debug(f"Logging initialized at level {level}")
    logger.debug(f"Log file: {os.path.join(log_dir, 'wizard.log')}")


def get_logger(name):
    """
    Get a logger for a specific module.

    Args:
        name: Module name or __name__

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def get_log_directory():
    """
    Get the directory for storing log files.

    Returns:
        Path to log directory
    """
    # Determine appropriate log directory for the platform
    if sys.platform == "win32":
        # Windows: %APPDATA%\CAPES Research Wizard\logs
        app_data = os.environ.get("APPDATA", "")
        base_dir = os.path.join(app_data, "CAPES Research Wizard")
    elif sys.platform == "darwin":
        # macOS: ~/Library/Logs/CAPES Research Wizard
        base_dir = os.path.expanduser("~/Library/Logs/CAPES Research Wizard")
    else:
        # Linux/Unix: ~/.local/share/capes-wizard/logs
        base_dir = os.path.expanduser("~/.local/share/capes-wizard")

    # Create logs directory
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    return log_dir
