"""Raw workflow event schema.

This module defines the WorkflowEventRaw model.

The model represents one raw workflow event record before standardization,
validation, and database loading.
"""

from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class WorkflowEventRaw(BaseModel):
    """Represent one raw workflow event record.

    This schema stores workflow event values as they are read from a source
    file. Workflow events describe the history of what happened to a sample
    during the pipeline.

    Fields:
        event_id: Raw unique identifier for the workflow event.
        sample_id: Raw sample identifier connected to the workflow event.
        event_status: Raw workflow status, such as received, reviewed,
            approved, repeated, rejected, or completed.
        event_timestamp_raw: Raw datetime when the workflow event happened.
        actor: Raw user, system, or process that created the event.
        message: Raw free-text workflow message or note.
        metadata: Ingestion metadata describing where the record came from.
    """

    event_id: str | None = None
    sample_id: str | None = None
    event_status: str | None = None
    event_timestamp_raw: str | None = None
    actor: str | None = None
    message: str | None = None

    metadata: IngestionMetadata