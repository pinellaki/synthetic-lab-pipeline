"""Rejected record writer utilities.

This module defines the RejectedRecordWriter class.

The writer saves rejected records to a CSV file so invalid or review-required
records are preserved for auditing, debugging, and later investigation.
"""

import csv
from pathlib import Path

from src.rejection.rejected_record import RejectedRecord


class RejectedRecordWriter:
    """Write rejected records to an output CSV file.

    The writer creates the output folder if it does not already exist and then
    writes rejected records using a fixed column order.

    This keeps rejection outputs consistent across pipeline runs.
    """

    def write_records(
        self,
        rejected_records: list[RejectedRecord],
        output_file_path: str,
    ) -> None:
        """Write rejected records to a CSV file.

        Args:
            rejected_records: List of rejected records to write.
            output_file_path: Path where the rejected-record CSV should be
                created.

        Returns:
            None.

        Notes:
            The output directory is created automatically if it does not exist.
            The method overwrites the output file if it already exists.
        """
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