from datetime import datetime

from pydantic import BaseModel


class RejectedRecord(BaseModel):
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