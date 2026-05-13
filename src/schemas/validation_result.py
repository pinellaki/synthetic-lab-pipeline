from pydantic import BaseModel


class ValidationResult(BaseModel):
    is_valid: bool
    rule_id: str | None = None
    severity: str | None = None
    message: str | None = None
    action: str | None = None