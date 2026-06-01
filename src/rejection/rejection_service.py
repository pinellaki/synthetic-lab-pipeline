"""Rejected record service.

This module defines the RejectionService class.

The service creates rejected-record objects from validation failures and
delegates writing rejected records to the RejectedRecordWriter.
"""

from datetime import datetime

from src.rejection.rejected_record import RejectedRecord
from src.rejection.rejected_record_writer import RejectedRecordWriter
from src.schemas.validation_result import ValidationResult


class RejectionService:
    """Create and write rejected records.

    This service connects validation results to rejected-record handling.

    It is responsible for:

    - creating a RejectedRecord from a failed ValidationResult
    - preserving source traceability information
    - delegating CSV writing to RejectedRecordWriter
    """

    def __init__(self, rejected_record_writer: RejectedRecordWriter) -> None:
        """Initialize the rejection service.

        Args:
            rejected_record_writer: Writer used to save rejected records.
        """
        self.rejected_record_writer = rejected_record_writer

    def create_rejected_record(
        self,
        source_file: str,
        run_id: str,
        validation_result: ValidationResult,
        source_record_id: str | None = None,
        source_row: int | None = None,
        source_sheet: str | None = None,
        source_page: int | None = None,
    ) -> RejectedRecord:
        """Create a rejected record from a validation result.

        Args:
            source_file: Source file where the rejected record came from.
            run_id: Identifier of the ingestion or pipeline run.
            validation_result: Validation result that caused the rejection or
                review decision.
            source_record_id: Optional identifier of the rejected source record.
            source_row: Optional row number in the source file.
            source_sheet: Optional sheet name for spreadsheet sources.
            source_page: Optional page number for paginated or PDF sources.

        Returns:
            A RejectedRecord containing the rejection reason, rule information,
            source traceability information, rejection timestamp, and run ID.

        Notes:
            If the validation result does not contain a rule ID, severity, or
            message, default fallback values are used.
        """
        return RejectedRecord(
            source_file=source_file,
            source_record_id=source_record_id,
            rule_id=validation_result.rule_id or "UNKNOWN",
            severity=validation_result.severity or "unknown",
            rejection_reason=validation_result.message or "No rejection reason provided.",
            rejected_at=datetime.utcnow(),
            run_id=run_id,
            source_row=source_row,
            source_sheet=source_sheet,
            source_page=source_page,
        )

    def write_rejected_records(
        self,
        rejected_records: list[RejectedRecord],
        output_file_path: str,
    ) -> None:
        """Write rejected records to an output file.

        Args:
            rejected_records: List of rejected records to write.
            output_file_path: Path where the rejected-record output should be
                created.

        Returns:
            None.
        """
        self.rejected_record_writer.write_records(
            rejected_records=rejected_records,
            output_file_path=output_file_path,
        )