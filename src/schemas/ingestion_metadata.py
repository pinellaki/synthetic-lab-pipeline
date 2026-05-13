from datetime import datetime

from pydantic import BaseModel


class IngestionMetadata(BaseModel):
    source_file: str
    run_id: str
    ingested_at: datetime

    source_row: int | None = None
    source_sheet: str | None = None
    source_page: int | None = None
    source_record_index: int | None = None