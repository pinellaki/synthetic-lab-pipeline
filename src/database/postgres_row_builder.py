"""Build database-ready rows from the M8 fake input data.

This module reuses the existing ingestion, standardization, and validation
components.

Only records that pass every required validation check are converted into
database-ready dictionaries.
"""

from datetime import UTC, datetime
from typing import Any

from src.database.postgres_reference_data import ANALYTE_ROWS
from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
    build_shipments,
    build_workflow_events,
)
from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.shipment_raw import ShipmentRaw
from src.schemas.workflow_event_raw import WorkflowEventRaw
from src.standardization.boolean_standardizer import BooleanStandardizer
from src.standardization.date_standardizer import DateStandardizer
from src.standardization.sample_id_standardizer import SampleIdStandardizer
from src.standardization.unit_standardizer import UnitStandardizer
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


def clean_optional_text(
    value: str | None,
    *,
    uppercase: bool = False,
    lowercase: bool = False,
) -> str | None:
    """Strip optional text and optionally normalize its letter case."""
    if value is None:
        return None

    cleaned_value = value.strip()

    if cleaned_value == "":
        return None

    if uppercase:
        return cleaned_value.upper()

    if lowercase:
        return cleaned_value.lower()

    return cleaned_value


def parse_optional_float(value: str | None) -> float | None:
    """Convert optional numeric text into a float."""
    if value is None or value.strip() == "":
        return None

    return float(value.replace(",", "."))


def parse_optional_int(value: str | None) -> int | None:
    """Convert optional integer text into an integer."""
    if value is None or value.strip() == "":
        return None

    return int(value)


def to_naive_utc(value: datetime) -> datetime:
    """Convert a datetime to UTC without timezone information.

    The PostgreSQL schema uses TIMESTAMP rather than TIMESTAMP WITH TIME ZONE.
    """
    if value.tzinfo is None:
        return value

    return value.astimezone(UTC).replace(tzinfo=None)


def sample_passes_validation(
    sample: SampleSubmissionRaw,
    collection_datetime: datetime | None,
    received_datetime: datetime | None,
    validator: SampleSubmissionValidator,
) -> bool:
    """Return True only when all sample validation checks pass."""
    validation_results = [
        validator.validate_required_sample_id(sample),
        validator.validate_required_subject_id(sample),
        validator.validate_collection_before_received(
            collection_datetime,
            received_datetime,
        ),
        validator.validate_temperature_is_numeric(
            sample.intake_temperature_c
        ),
    ]

    return all(result.is_valid for result in validation_results)


def build_valid_sample_rows() -> list[dict[str, Any]]:
    """Build clean PostgreSQL rows from valid fake sample records."""
    sample_id_standardizer = SampleIdStandardizer()
    boolean_standardizer = BooleanStandardizer()
    date_standardizer = DateStandardizer()
    validator = SampleSubmissionValidator()

    valid_rows: list[dict[str, Any]] = []

    for sample in build_sample_submissions():
        collection_datetime = date_standardizer.standardize(
            sample.collection_datetime
        )
        received_datetime = date_standardizer.standardize(
            sample.received_datetime
        )

        if not sample_passes_validation(
            sample=sample,
            collection_datetime=collection_datetime,
            received_datetime=received_datetime,
            validator=validator,
        ):
            continue

        standardized_sample_id = sample_id_standardizer.standardize(
            sample.sample_id
        )

        if standardized_sample_id is None:
            continue

        valid_rows.append(
            {
                "sample_id": standardized_sample_id,
                "subject_id": clean_optional_text(
                    sample.subject_id,
                    uppercase=True,
                ),
                "collection_site_code": clean_optional_text(
                    sample.collection_site,
                    uppercase=True,
                ),
                "sample_type": clean_optional_text(
                    sample.sample_type,
                    uppercase=True,
                ),
                "collection_datetime": collection_datetime,
                "received_datetime": received_datetime,
                "priority": clean_optional_text(
                    sample.priority,
                    lowercase=True,
                ),
                "consent_recorded": boolean_standardizer.standardize(
                    sample.consent_recorded
                ),
                "intake_temperature_c": parse_optional_float(
                    sample.intake_temperature_c
                ),
                "operator_notes": clean_optional_text(
                    sample.operator_notes
                ),
                "source_file": sample.metadata.source_file,
                "source_row": sample.metadata.source_row,
                "ingested_at": to_naive_utc(
                    sample.metadata.ingested_at
                ),
            }
        )

    return valid_rows


def assay_result_passes_validation(
    assay_result: AssayResultRaw,
    validator: AssayResultValidator,
) -> bool:
    """Return True only when every assay-result validation passes."""
    validation_results = [
        validator.validate_required_result_id(assay_result),
        validator.validate_required_sample_id(assay_result),
        validator.validate_required_analyte_code(assay_result),
        validator.validate_required_unit(assay_result),
        validator.validate_result_value_is_numeric(assay_result),
        validator.validate_result_value_is_non_negative(assay_result),
    ]

    return all(result.is_valid for result in validation_results)


def build_valid_assay_result_rows() -> list[dict[str, Any]]:
    """Build clean PostgreSQL rows from valid fake assay-result records."""
    sample_id_standardizer = SampleIdStandardizer()
    boolean_standardizer = BooleanStandardizer()
    date_standardizer = DateStandardizer()
    unit_standardizer = UnitStandardizer()
    validator = AssayResultValidator()

    accepted_sample_ids = {
        row["sample_id"]
        for row in build_valid_sample_rows()
    }

    known_analyte_codes = {
        row["analyte_code"]
        for row in ANALYTE_ROWS
    }

    valid_rows: list[dict[str, Any]] = []

    for assay_result in build_assay_results():
        if not assay_result_passes_validation(
            assay_result=assay_result,
            validator=validator,
        ):
            continue

        result_id = clean_optional_text(
            assay_result.result_id,
            uppercase=True,
        )
        sample_id = sample_id_standardizer.standardize(
            assay_result.sample_id
        )
        analyte_code = clean_optional_text(
            assay_result.analyte_code,
            uppercase=True,
        )

        if result_id is None or sample_id is None or analyte_code is None:
            continue

        if sample_id not in accepted_sample_ids:
            continue

        if analyte_code not in known_analyte_codes:
            continue

        standardized_unit = unit_standardizer.standardize(
            assay_result.unit_raw
        )

        if standardized_unit is None:
            standardized_unit = clean_optional_text(
                assay_result.unit_raw
            )

        valid_rows.append(
            {
                "result_id": result_id,
                "sample_id": sample_id,
                "analyte_code": analyte_code,
                "result_value": parse_optional_float(
                    assay_result.result_value_raw
                ),
                "unit": standardized_unit,
                "run_datetime": date_standardizer.standardize(
                    assay_result.run_datetime_raw
                ),
                "instrument_id": clean_optional_text(
                    assay_result.instrument_id,
                    uppercase=True,
                ),
                "analyst": clean_optional_text(
                    assay_result.analyst
                ),
                "qc_status": clean_optional_text(
                    assay_result.qc_status,
                    uppercase=True,
                ),
                "review_status": clean_optional_text(
                    assay_result.review_status,
                    lowercase=True,
                ),
                "approved_at": date_standardizer.standardize(
                    assay_result.approved_at_raw
                ),
                "version": parse_optional_int(
                    assay_result.version
                ),
                "is_current": boolean_standardizer.standardize(
                    assay_result.is_current_raw
                ),
                "deleted_at": date_standardizer.standardize(
                    assay_result.deleted_at_raw
                ),
                "source_file": assay_result.metadata.source_file,
                "source_row": assay_result.metadata.source_row,
                "ingested_at": to_naive_utc(
                    assay_result.metadata.ingested_at
                ),
            }
        )

    return valid_rows


def shipment_passes_validation(
    shipment: ShipmentRaw,
    shipped_at: datetime | None,
    received_at: datetime | None,
    api_updated_at: datetime | None,
) -> bool:
    """Return True when a shipment has valid basic database fields.

    A dedicated ShipmentValidator does not exist yet, so the one-time loader
    applies only the minimal checks required for safe database insertion.
    """
    if clean_optional_text(shipment.shipment_id) is None:
        return False

    if clean_optional_text(shipment.sample_id) is None:
        return False

    if shipped_at is None:
        return False

    if received_at is not None and shipped_at > received_at:
        return False

    if (
        shipment.received_at_raw is not None
        and shipment.received_at_raw.strip() != ""
        and received_at is None
    ):
        return False

    if (
        shipment.api_updated_at_raw is not None
        and shipment.api_updated_at_raw.strip() != ""
        and api_updated_at is None
    ):
        return False

    if (
        shipment.condition_temp_c_raw is not None
        and shipment.condition_temp_c_raw.strip() != ""
    ):
        try:
            parse_optional_float(shipment.condition_temp_c_raw)
        except ValueError:
            return False

    return True


def build_valid_shipment_rows() -> list[dict[str, Any]]:
    """Build clean PostgreSQL rows from valid fake shipment records."""
    sample_id_standardizer = SampleIdStandardizer()
    date_standardizer = DateStandardizer()

    accepted_sample_ids = {
        row["sample_id"]
        for row in build_valid_sample_rows()
    }

    valid_rows: list[dict[str, Any]] = []

    for shipment in build_shipments():
        shipped_at = date_standardizer.standardize(
            shipment.shipped_at_raw
        )
        received_at = date_standardizer.standardize(
            shipment.received_at_raw
        )
        api_updated_at = date_standardizer.standardize(
            shipment.api_updated_at_raw
        )

        if not shipment_passes_validation(
            shipment=shipment,
            shipped_at=shipped_at,
            received_at=received_at,
            api_updated_at=api_updated_at,
        ):
            continue

        shipment_id = clean_optional_text(
            shipment.shipment_id,
            uppercase=True,
        )
        sample_id = sample_id_standardizer.standardize(
            shipment.sample_id
        )

        if shipment_id is None or sample_id is None:
            continue

        if sample_id not in accepted_sample_ids:
            continue

        source_record_index = (
            shipment.metadata.source_record_index
            if shipment.metadata.source_record_index is not None
            else shipment.metadata.source_row
        )

        valid_rows.append(
            {
                "shipment_id": shipment_id,
                "sample_id": sample_id,
                "courier": clean_optional_text(
                    shipment.courier,
                    uppercase=True,
                ),
                "shipped_at": shipped_at,
                "received_at": received_at,
                "condition_temp_c": parse_optional_float(
                    shipment.condition_temp_c_raw
                ),
                "status": clean_optional_text(
                    shipment.status,
                    lowercase=True,
                ),
                "api_updated_at": api_updated_at,
                "source_file": shipment.metadata.source_file,
                "source_page": shipment.metadata.source_page,
                "source_record_index": source_record_index,
                "ingested_at": to_naive_utc(
                    shipment.metadata.ingested_at
                ),
            }
        )

    return valid_rows


def workflow_event_passes_validation(
    workflow_event: WorkflowEventRaw,
    event_timestamp: datetime | None,
) -> bool:
    """Return True when a workflow event has valid required fields."""
    if clean_optional_text(workflow_event.event_id) is None:
        return False

    if clean_optional_text(workflow_event.sample_id) is None:
        return False

    if clean_optional_text(workflow_event.event_status) is None:
        return False

    if event_timestamp is None:
        return False

    return True


def build_valid_workflow_event_rows() -> list[dict[str, Any]]:
    """Build clean PostgreSQL rows from valid fake workflow events."""
    sample_id_standardizer = SampleIdStandardizer()
    date_standardizer = DateStandardizer()

    accepted_sample_ids = {
        row["sample_id"]
        for row in build_valid_sample_rows()
    }

    valid_rows: list[dict[str, Any]] = []

    for workflow_event in build_workflow_events():
        event_timestamp = date_standardizer.standardize(
            workflow_event.event_timestamp_raw
        )

        if not workflow_event_passes_validation(
            workflow_event=workflow_event,
            event_timestamp=event_timestamp,
        ):
            continue

        event_id = clean_optional_text(
            workflow_event.event_id,
            uppercase=True,
        )
        sample_id = sample_id_standardizer.standardize(
            workflow_event.sample_id
        )

        if event_id is None or sample_id is None:
            continue

        if sample_id not in accepted_sample_ids:
            continue

        valid_rows.append(
            {
                "event_id": event_id,
                "sample_id": sample_id,
                "event_status": clean_optional_text(
                    workflow_event.event_status,
                    lowercase=True,
                ),
                "event_timestamp": event_timestamp,
                "actor": clean_optional_text(
                    workflow_event.actor
                ),
                "message": clean_optional_text(
                    workflow_event.message
                ),
                "source_file": workflow_event.metadata.source_file,
                "source_row": workflow_event.metadata.source_row,
                "ingested_at": to_naive_utc(
                    workflow_event.metadata.ingested_at
                ),
            }
        )

    return valid_rows