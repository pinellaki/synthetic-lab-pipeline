"""Raw sample submission schema.

This module defines the SampleSubmissionRaw model.

The model represents one raw sample submission record before full
standardization, validation, and database loading.
"""

from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class SampleSubmissionRaw(BaseModel):
    """Represent one raw sample submission record.

    This schema stores raw values as they are read from the source file.
    Most fields are optional because raw input files may contain missing,
    incomplete, or malformed values.

    The model stores sample identifiers, subject identifiers, collection
    details, received datetime values, priority, consent information, intake
    temperature, operator notes, and ingestion metadata.
    """

    sample_id: str | None = None
    subject_id: str | None = None
    collection_site: str | None = None
    sample_type: str | None = None
    collection_datetime: str | None = None
    received_datetime: str | None = None
    priority: str | None = None
    consent_recorded: str | None = None
    intake_temperature_c: str | None = None
    operator_notes: str | None = None

    metadata: IngestionMetadata