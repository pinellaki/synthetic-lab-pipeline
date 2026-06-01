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

    The model stores event identifiers, sample identifiers, event status,
    event timestamp, actor information, workflow messages, and ingestion
    metadata.
    """

    event_id: str | None = None
    sample_id: str | None = None
    event_status: str | None = None
    event_timestamp_raw: str | None = None
    actor: str | None = None
    message: str | None = None

    metadata: IngestionMetadata