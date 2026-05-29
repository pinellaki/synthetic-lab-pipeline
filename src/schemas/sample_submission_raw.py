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

    Attributes:
        sample_id: Raw sample identifier from the source file.
        subject_id: Raw subject identifier connected to the sample.
        collection_site: Raw collection site value.
        sample_type: Raw sample type value.
        collection_datetime: Raw collection datetime value as text.
        received_datetime: Raw received datetime value as text.
        priority: Raw priority value.
        consent_recorded: Raw consent value before boolean standardization.
        intake_temperature_c: Raw intake temperature value before numeric
            validation.
        operator_notes: Free-text notes entered by the operator.
        metadata: Ingestion metadata describing where the record came from.
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