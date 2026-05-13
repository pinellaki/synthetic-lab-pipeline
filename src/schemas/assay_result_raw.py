from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class AssayResultRaw(BaseModel):
    result_id: str | None = None
    sample_id: str | None = None
    analyte_code: str | None = None
    result_value_raw: str | None = None
    unit_raw: str | None = None
    run_datetime_raw: str | None = None
    instrument_id: str | None = None
    analyst: str | None = None
    qc_status: str | None = None
    review_status: str | None = None
    approved_at_raw: str | None = None
    version: str | None = None
    is_current_raw: str | None = None
    deleted_at_raw: str | None = None

    metadata: IngestionMetadata