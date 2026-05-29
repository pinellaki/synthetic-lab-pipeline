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

    The model stores the validation status, rule identifier, severity level,
    human-readable message, and recommended action.
    """

    is_valid: bool
    rule_id: str | None = None
    severity: str | None = None
    message: str | None = None
    action: str | None = None