from pathlib import Path
import csv


class CsvReader:
    def read_rows_as_dicts(self, file_path: str) -> list[dict[str, str]]:
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            return [dict(row) for row in reader]