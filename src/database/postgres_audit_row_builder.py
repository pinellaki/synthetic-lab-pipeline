"""Build PostgreSQL audit rows from M8 validation results.

This module converts the existing M8 validation outcomes and rejected-record
objects into dictionaries that match the PostgreSQL audit tables:

- validation_result
- rejected_record

The functions only prepare data in memory. They do not insert anything into
PostgreSQL.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from src.pipeline.sample_data_rejection_test import build_rejected_records
from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
)
from src.pipeline.sample_data_validation_test import (
    validate_assay_result,
    validate_sample_submission,
)
from src.schemas.validation_result import ValidationResult
from src.standardization.date_standardizer import DateStandardizer
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


SAMPLE_RULE_METADATA = [
    ("S1", "sample_id"),
    ("S4", "subject_id"),
    ("S8", "collection_datetime"),
    ("S10", "intake_temperature_c"),
]

ASSAY_RULE_METADATA = [
    ("R1", "result_id"),
    ("R2", "sample_id"),
    ("R4", "analyte_code"),
    ("R9", "unit"),
    ("R6", "result_value"),
    ("R7", "result_value"),
]


def clean_optional_text(value: str | None) -> str | None:
    """Strip optional text and return None for missing or empty values."""
    if value is None:
        return None

    cleaned_value = value.strip()

    if cleaned_value == "":
        return None

    return cleaned_value


def to_naive_utc(value: datetime) -> datetime:
    """Convert a datetime to UTC without timezone information."""
    if value.tzinfo is None:
        return value

    return value.astimezone(UTC).replace(tzinfo=None)


def create_stable_id(prefix: str, *parts: object) -> str:
    """Create a stable identifier from a prefix and source values."""
    normalized_parts = [
        "" if part is None else str(part)
        for part in parts
    ]

    unique_value = "|".join([prefix, *normalized_parts])
    generated_uuid = uuid5(NAMESPACE_URL, unique_value)

    return f"{prefix}-{generated_uuid}"


def build_validation_result_row(
    *,
    source_table: str,
    source_record_id: str | None,
    source_field: str,
    source_file: str,
    source_row: int | None,
    rule_id: str,
    validation_result: ValidationResult,
) -> dict[str, Any]:
    """Convert one validation outcome into a PostgreSQL row."""
    validation_result_id = create_stable_id(
        "VAL",
        source_table,
        source_file,
        source_row,
        source_record_id,
        rule_id,
    )

    return {
        "validation_result_id": validation_result_id,
        "rule_id": rule_id,
        "source_table": source_table,
        "source_record_id": clean_optional_text(source_record_id),
        "source_field": source_field,
        "is_valid": validation_result.is_valid,
        "severity": validation_result.severity,
        "action": validation_result.action,
        "message": validation_result.message,
        "source_file": source_file,
        "source_row": source_row,
    }


def build_sample_validation_result_rows() -> list[dict[str, Any]]:
    """Build validation-result rows for all fake sample checks."""
    validator = SampleSubmissionValidator()
    date_standardizer = DateStandardizer()

    validation_rows: list[dict[str, Any]] = []

    for sample in build_sample_submissions():
        results = validate_sample_submission(
            sample_submission=sample,
            validator=validator,
            date_standardizer=date_standardizer,
        )

        if len(results) != len(SAMPLE_RULE_METADATA):
            raise RuntimeError(
                "Sample validation result count does not match rule metadata."
            )

        for (rule_id, source_field), result in zip(
            SAMPLE_RULE_METADATA,
            results,
            strict=True,
        ):
            validation_rows.append(
                build_validation_result_row(
                    source_table="sample",
                    source_record_id=sample.sample_id,
                    source_field=source_field,
                    source_file=sample.metadata.source_file,
                    source_row=sample.metadata.source_row,
                    rule_id=rule_id,
                    validation_result=result,
                )
            )

    return validation_rows


def build_assay_validation_result_rows() -> list[dict[str, Any]]:
    """Build validation-result rows for all fake assay-result checks."""
    validator = AssayResultValidator()

    validation_rows: list[dict[str, Any]] = []

    for assay_result in build_assay_results():
        results = validate_assay_result(
            assay_result=assay_result,
            validator=validator,
        )

        if len(results) != len(ASSAY_RULE_METADATA):
            raise RuntimeError(
                "Assay validation result count does not match rule metadata."
            )

        for (rule_id, source_field), result in zip(
            ASSAY_RULE_METADATA,
            results,
            strict=True,
        ):
            validation_rows.append(
                build_validation_result_row(
                    source_table="assay_result",
                    source_record_id=assay_result.result_id,
                    source_field=source_field,
                    source_file=assay_result.metadata.source_file,
                    source_row=assay_result.metadata.source_row,
                    rule_id=rule_id,
                    validation_result=result,
                )
            )

    return validation_rows


def build_validation_result_rows() -> list[dict[str, Any]]:
    """Build all sample and assay validation-result rows."""
    return [
        *build_sample_validation_result_rows(),
        *build_assay_validation_result_rows(),
    ]


def build_raw_payload_lookup() -> dict[tuple[str, int | None], str]:
    """Map each source file and row to its original raw JSON payload."""
    raw_payload_lookup: dict[tuple[str, int | None], str] = {}

    for sample in build_sample_submissions():
        key = (
            sample.metadata.source_file,
            sample.metadata.source_row,
        )
        raw_payload_lookup[key] = sample.model_dump_json()

    for assay_result in build_assay_results():
        key = (
            assay_result.metadata.source_file,
            assay_result.metadata.source_row,
        )
        raw_payload_lookup[key] = assay_result.model_dump_json()

    return raw_payload_lookup


def infer_source_table(source_file: str) -> str:
    """Infer the source database table from the fake source filename."""
    if source_file == "sample_submissions.csv":
        return "sample"

    if source_file == "assay_results.csv":
        return "assay_result"

    return "unknown"


def build_rejected_record_rows() -> list[dict[str, Any]]:
    """Build PostgreSQL rejected-record rows from M8 rejections."""
    raw_payload_lookup = build_raw_payload_lookup()
    rejected_rows: list[dict[str, Any]] = []

    for rejected_record in build_rejected_records():
        source_table = infer_source_table(
            rejected_record.source_file
        )

        rejected_record_id = create_stable_id(
            "REJ",
            source_table,
            rejected_record.source_file,
            rejected_record.source_row,
            rejected_record.source_record_id,
            rejected_record.rule_id,
        )

        raw_payload = raw_payload_lookup.get(
            (
                rejected_record.source_file,
                rejected_record.source_row,
            )
        )

        rejected_rows.append(
            {
                "rejected_record_id": rejected_record_id,
                "source_table": source_table,
                "source_record_id": clean_optional_text(
                    rejected_record.source_record_id
                ),
                "source_file": rejected_record.source_file,
                "source_row": rejected_record.source_row,
                "source_sheet": rejected_record.source_sheet,
                "source_page": rejected_record.source_page,
                "rule_id": rejected_record.rule_id,
                "severity": rejected_record.severity,
                "rejection_reason": rejected_record.rejection_reason,
                "raw_payload": raw_payload,
                "run_id": rejected_record.run_id,
                "rejected_at": to_naive_utc(
                    rejected_record.rejected_at
                ),
            }
        )

    return rejected_rows