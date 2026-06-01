"""CSV ingestion utilities.

This module defines the CsvReader class.

The CsvReader reads CSV files and converts each row into a dictionary. This is
useful because later pipeline steps can work with consistent Python data
structures instead of reading files directly.
"""

import csv
from pathlib import Path


class CsvReader:
    """Read CSV files into lists of dictionaries.

    The reader uses ``csv.DictReader`` so each CSV row is returned as a
    dictionary where:

    - keys are column names
    - values are cell values from that row

    The reader uses ``utf-8-sig`` encoding so it can handle CSV files that
    contain a UTF-8 byte order mark.
    """

    def read_rows_as_dicts(self, file_path: str) -> list[dict[str, str]]:
        """Read a CSV file and return its rows as dictionaries.

        Args:
            file_path: Path to the CSV file to read.

        Returns:
            A list of dictionaries. Each dictionary represents one CSV row.

        Example:
            If the CSV contains columns ``sample_id`` and ``subject_id``,
            each returned row will look like::

                {
                    "sample_id": "SMP-001",
                    "subject_id": "SUBJ-001",
                }

        Notes:
            This method only reads the file. It does not validate,
            standardize, or transform the data.
        """
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [dict(row) for row in reader]