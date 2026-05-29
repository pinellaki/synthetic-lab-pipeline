"""Logging configuration utilities.

This module defines the LoggingConfig class.

The class creates configured loggers for the Synthetic Lab Pipeline project.
A logger is used to record information, warnings, and errors while the pipeline
runs.
"""

import logging


class LoggingConfig:
    """Create configured logger instances for the pipeline.

    The logger writes messages to the console using a standard format that
    includes:

    - timestamp
    - log level
    - logger name
    - log message

    The class also avoids adding duplicate handlers when the same logger is
    requested more than once.
    """

    def create_logger(self, logger_name: str, logging_level: str) -> logging.Logger:
        """Create or return a configured logger.

        Args:
            logger_name: Name of the logger to create or retrieve.
            logging_level: Logging level to apply, such as ``INFO``, ``DEBUG``,
                ``WARNING``, or ``ERROR``.

        Returns:
            A configured ``logging.Logger`` instance.

        Notes:
            The method checks whether the logger already has handlers before
            adding a new console handler. This prevents duplicate log messages
            when the function is called multiple times for the same logger.
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging_level)

        if not logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging_level)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )

            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger