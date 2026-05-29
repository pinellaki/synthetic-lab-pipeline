"""Validation result schema.

This module defines the ValidationResult model.

The model represents the outcome of one validation rule. It is used by
validators to return a consistent result containing the rule status, severity,
message, and action.
"""

from pydantic import BaseModel


class ValidationResult(BaseModel):
    """Represent the result of one validation rule.

    A ValidationResult is returned by validation functions to describe whether
    a rule passed or failed.

    Fields:
        is_valid: True if the validation rule passed, False if it failed.
        rule_id: Identifier of the validation rule that was evaluated.
        severity: Severity level of the rule failure, such as medium, high, or
            critical.
        message: Human-readable explanation of the validation result.
        action: Recommended action when the rule fails, such as reject, review,
            warn, or standardize.
    """

    is_valid: bool
    rule_id: str | None = None
    severity: str | None = None
    message: str | None = None
    action: str | None = None
