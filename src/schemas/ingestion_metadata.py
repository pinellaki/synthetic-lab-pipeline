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

    The model stores the source file, ingestion run ID, ingestion timestamp,
    source row, source sheet, source page, and source record index when those
    values are available.
    """

    source_file: str
    run_id: str
    ingested_at: datetime

    source_row: int | None = None
    source_sheet: str | None = None
    source_page: int | None = None
    source_record_index: int | None = None