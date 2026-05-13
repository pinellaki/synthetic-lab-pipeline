import csv
from pathlib import Path

from src.rejection.rejected_record import RejectedRecord


class RejectedRecordWriter:
    def write_records(
        self,
        rejected_records: list[RejectedRecord],
        output_file_path: str,
    ) -> None:
        path = Path(output_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open(mode="w", encoding="utf-8", newline="") as output_file:
            writer = csv.DictWriter(
                output_file,
                fieldnames=[
                    "source_file",
                    "source_record_id",
                    "rule_id",
                    "severity",
                    "rejection_reason",
                    "rejected_at",
                    "run_id",
                    "source_row",
                    "source_sheet",
                    "source_page",
                ],
            )

            writer.writeheader()

            for rejected_record in rejected_records:
                writer.writerow(rejected_record.model_dump())