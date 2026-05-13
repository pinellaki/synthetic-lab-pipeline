import logging


class LoggingConfig:
    def create_logger(self, logger_name: str, logging_level: str) -> logging.Logger:
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