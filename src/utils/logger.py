"""Utility module for setting up a logger to log messages to a file."""
import logging


def setup_logger(*, name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Set up a logger with the specified name, log file, and logging level.

    Args:
        name (str): The name of the logger.
        log_file (str): The file path where the log messages will be saved.
        level: The logging level (e.g., logging.INFO, logging.DEBUG).

    Returns:
        logging.Logger: A configured logger instance.
    """
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger
