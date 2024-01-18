"""Implement for kafka log."""
import logging


class KafkaLogFilter(logging.Filter):
    """Implement for kafka log."""

    def __init__(self, levels):
        super().__init__()
        self.levels = levels

    def filter(self, record):
        """Filter warning log."""
        # Return False if the log level is WARNING, True otherwise
        return record.levelno in self.levels
