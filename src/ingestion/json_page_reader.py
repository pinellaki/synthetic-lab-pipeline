"""JSON ingestion utilities.

This module defines the JsonPageReader class.

The JsonPageReader reads JSON files and can follow simple pagination between
JSON pages. It is useful for source data exported from APIs where records are
split across multiple JSON files.
"""

import json
from pathlib import Path
from typing import Any


class JsonPageReader:
    """Read JSON files and paginated JSON records.

    The reader supports two operations:

    - reading one JSON file as a dictionary
    - reading records from multiple linked JSON pages

    Paginated files are expected to contain:

    - ``data``: a list of records
    - ``next_page``: the filename of the next page, or None
    """

    def read_json_file(self, file_path: str) -> dict[str, Any]:
        """Read one JSON file and return its content.

        Args:
            file_path: Path to the JSON file to read.

        Returns:
            The parsed JSON content as a dictionary.

        Notes:
            This method only reads and parses the JSON file. It does not
            validate or standardize the records.
        """
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8") as json_file:
            return json.load(json_file)

    def read_paginated_records(self, first_page_path: str) -> list[dict[str, Any]]:
        """Read all records from a paginated JSON file sequence.

        Args:
            first_page_path: Path to the first JSON page.

        Returns:
            A list of record dictionaries collected from all pages.

        Pagination logic:
            The method starts from the first page, reads records from the
            ``data`` field, then follows the ``next_page`` value until no next
            page exists.

        Example:
            If ``page_1.json`` contains ``"next_page": "page_2.json"``, the
            reader will load ``page_2.json`` from the same folder.
        """
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