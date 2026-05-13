from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class SampleSubmissionRaw(BaseModel):
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