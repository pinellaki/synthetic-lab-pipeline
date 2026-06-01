"""Custom exceptions for the Synthetic Lab Pipeline.

This module defines project-specific exception classes.

Custom exceptions make pipeline errors easier to understand, catch, and debug.
"""


class PipelineException(Exception):
    """Represent a custom pipeline error.

    This exception can store both a human-readable error message and an
    optional validation rule identifier.

    Args:
        message: Human-readable error message.
        rule_id: Optional validation rule identifier related to the error.

    Attributes:
        message: Human-readable error message.
        rule_id: Optional validation rule identifier.
    """

    def __init__(self, message: str, rule_id: str | None = None) -> None:
        """Initialize a pipeline exception.

        Args:
            message: Human-readable error message.
            rule_id: Optional validation rule identifier related to the error.
        """
        self.message = message
        self.rule_id = rule_id
        super().__init__(self.message)