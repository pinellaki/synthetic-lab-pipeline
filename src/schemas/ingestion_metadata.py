"""Ingestion metadata schema.

This module defines the IngestionMetadata model.

The model stores traceability information for records loaded into the pipeline.
It helps identify where each record came from, which ingestion run created it,
and where the original value can be found in the source file.
"""

from datetime import datetime

from pydantic import BaseModel


class IngestionMetadata(BaseModel):
    """Store source and ingestion traceability information.

    This schema is attached to raw records so every record can be traced back
    to its original source.

    Attributes:
        source_file: Name or path of the source file that provided the record.
        run_id: Identifier of the ingestion run that processed the record.
        ingested_at: Datetime when the record was ingested.
        source_row: Row number in the source file, when available.
        source_sheet: Sheet name for spreadsheet sources, when available.
        source_page: Page number for PDF or paginated sources, when available.
        source_record_index: Position of the record inside a page, payload, or
            nested source structure, when available.
    """

    source_file: str
    run_id: str
    ingested_at: datetime

    source_row: int | None = None
    source_sheet: str | None = None
    source_page: int | None = None
    source_record_index: int | None = None