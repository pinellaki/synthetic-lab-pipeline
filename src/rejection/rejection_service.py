from datetime import datetime

from src.rejection.rejected_record import RejectedRecord
from src.rejection.rejected_record_writer import RejectedRecordWriter
from src.schemas.validation_result import ValidationResult


class RejectionService:
    def __init__(self, rejected_record_writer: RejectedRecordWriter) -> None:
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
        self.rejected_record_writer.write_records(
            rejected_records=rejected_records,
            output_file_path=output_file_path,
        )