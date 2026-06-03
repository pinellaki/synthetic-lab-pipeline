"""M8 sample data rejection test.

This script validates fake M8 records, converts failed validation results into
RejectedRecord objects, and writes them to a rejected-record CSV file.

It does not use real company data.
It does not load data into PostgreSQL.
It only verifies that failed validations can be transformed into audit-friendly
rejected records.
"""

from pathlib import Path

from src.ingestion.csv_reader import CsvReader
from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
)
from src.pipeline.sample_data_validation_test import (
    validate_assay_result,
    validate_sample_submission,
)
from src.rejection.rejected_record import RejectedRecord
from src.rejection.rejected_record_writer import RejectedRecordWriter
from src.rejection.rejection_service import RejectionService
from src.schemas.validation_result import ValidationResult
from src.standardization.date_standardizer import DateStandardizer
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


OUTPUT_FILE = Path("data/rejected/m8_rejected_records.csv")


def create_rejections_for_record(
    rejection_service: RejectionService,
    validation_results: list[ValidationResult],
    source_file: str,
    run_id: str,
    source_record_id: str | None,
    source_row: int | None,
) -> list[RejectedRecord]:
    """Create rejected records for failed validation results.

    Args:
        rejection_service: Service used to create rejected records.
        validation_results: Validation results for one source record.
        source_file: Source file where the record came from.
        run_id: Identifier of the fake M8 pipeline run.
        source_record_id: Identifier of the source record, if available.
        source_row: Source row number, if available.

    Returns:
        RejectedRecord objects created from failed validation results.
    """
    rejected_records: list[RejectedRecord] = []

    for validation_result in validation_results:
        if validation_result.is_valid:
            continue

        rejected_records.append(
            rejection_service.create_rejected_record(
                source_file=source_file,
                run_id=run_id,
                validation_result=validation_result,
                source_record_id=source_record_id,
                source_row=source_row,
            )
        )

    return rejected_records


def build_rejected_records() -> list[RejectedRecord]:
    """Validate fake records and return rejected records for failed checks."""
    sample_validator = SampleSubmissionValidator()
    assay_validator = AssayResultValidator()
    date_standardizer = DateStandardizer()

    rejection_service = RejectionService(
        rejected_record_writer=RejectedRecordWriter()
    )

    rejected_records: list[RejectedRecord] = []

    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()

    for sample_submission in sample_submissions:
        validation_results = validate_sample_submission(
            sample_submission=sample_submission,
            validator=sample_validator,
            date_standardizer=date_standardizer,
        )

        rejected_records.extend(
            create_rejections_for_record(
                rejection_service=rejection_service,
                validation_results=validation_results,
                source_file=sample_submission.metadata.source_file,
                run_id=sample_submission.metadata.run_id,
                source_record_id=sample_submission.sample_id,
                source_row=sample_submission.metadata.source_row,
            )
        )

    for assay_result in assay_results:
        validation_results = validate_assay_result(
            assay_result=assay_result,
            validator=assay_validator,
        )

        rejected_records.extend(
            create_rejections_for_record(
                rejection_service=rejection_service,
                validation_results=validation_results,
                source_file=assay_result.metadata.source_file,
                run_id=assay_result.metadata.run_id,
                source_record_id=assay_result.result_id,
                source_row=assay_result.metadata.source_row,
            )
        )

    return rejected_records


def main() -> None:
    """Create and write rejected records from fake validation failures."""
    rejected_record_writer = RejectedRecordWriter()
    rejection_service = RejectionService(
        rejected_record_writer=rejected_record_writer
    )

    rejected_records = build_rejected_records()

    rejection_service.write_rejected_records(
        rejected_records=rejected_records,
        output_file_path=str(OUTPUT_FILE),
    )

    csv_reader = CsvReader()
    written_rows = csv_reader.read_rows_as_dicts(str(OUTPUT_FILE))

    print("M8 sample data rejection test")
    print("=============================")
    print(f"Rejected records created: {len(rejected_records)}")
    print(f"Rejected records written: {len(written_rows)}")
    print(f"Output file: {OUTPUT_FILE}")

    expected_rejected_count = 7

    if len(rejected_records) != expected_rejected_count:
        raise RuntimeError(
            "Unexpected rejected record count. "
            f"Expected {expected_rejected_count}, got {len(rejected_records)}."
        )

    if len(written_rows) != expected_rejected_count:
        raise RuntimeError(
            "Unexpected written rejected row count. "
            f"Expected {expected_rejected_count}, got {len(written_rows)}."
        )

    print("Rejection test passed.")


if __name__ == "__main__":
    main()