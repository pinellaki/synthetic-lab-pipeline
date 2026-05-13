import json
from pathlib import Path
from typing import Any


class JsonPageReader:
    def read_json_file(self, file_path: str) -> dict[str, Any]:
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def read_paginated_records(self, first_page_path: str) -> list[dict[str, Any]]:
        current_page_path = Path(first_page_path)
        all_records: list[dict[str, Any]] = []

        while current_page_path is not None:
            page_content = self.read_json_file(str(current_page_path))
            page_records = page_content.get("data", [])

            all_records.extend(page_records)

            next_page = page_content.get("next_page")

            if next_page is None:
                break

            current_page_path = current_page_path.parent / next_page

        return all_records