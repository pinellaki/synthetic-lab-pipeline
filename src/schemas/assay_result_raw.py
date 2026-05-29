"""Raw assay result schema.

This module defines the AssayResultRaw model.

The model represents one raw assay result record before standardization,
validation, and database loading.
"""

from pydantic import BaseModel

from src.schemas.ingestion_metadata import IngestionMetadata


class AssayResultRaw(BaseModel):
    """Represent one raw assay result record.

    This schema stores assay result values as they are read from the source
    file. Most fields are optional because raw lab data can be incomplete,
    malformed, or pending review.

    Attributes:
        result_id: Raw unique identifier for the assay result.
        sample_id: Raw sample identifier connected to the result.
        analyte_code: Raw analyte or test code.
        result_value_raw: Raw result value before numeric standardization.
        unit_raw: Raw measurement unit before unit standardization.
        run_datetime_raw: Raw datetime when the assay was run.
        instrument_id: Identifier of the instrument used for the assay.
        analyst: Name or identifier of the analyst.
        qc_status: Raw quality control status.
        review_status: Raw review or approval status.
        approved_at_raw: Raw approval datetime value.
        version: Raw version value for repeated or updated results.
        is_current_raw: Raw value indicating whether this is the current result.
        deleted_at_raw: Raw deletion datetime value, if the result was deleted.
        metadata: Ingestion metadata describing where the record came from.
    """

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