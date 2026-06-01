"""Rejected record schema.

This module defines the RejectedRecord model.

Rejected records are used to keep track of source records that failed
validation or need manual review. The model preserves the rejection reason,
rule information, source location, and ingestion run information.
"""

from datetime import datetime

from pydantic import BaseModel


class RejectedRecord(BaseModel):
    """Represent one rejected or review-required source record.

    This model stores enough information to trace a rejected record back to its
    original source file and explain why it was rejected.

    The model includes source file information, source row or page details,
    validation rule information, rejection severity, rejection reason, rejection
    timestamp, and ingestion run identifier.
    """

    source_file: str
    source_record_id: str | None = None
    rule_id: str
    severity: str
    rejection_reason: str
    rejected_at: datetime
    run_id: str

    source_row: int | None = None
    source_sheet: str | None = None
    source_page: int | None = None