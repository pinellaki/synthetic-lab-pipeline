"""Excel ingestion utilities.

This module defines the ExcelReader class.

The ExcelReader reads Excel workbooks and converts sheets into Python
dictionaries. This allows later pipeline steps to process Excel data in the
same style as CSV data.
"""

from pathlib import Path

import pandas as pd


class ExcelReader:
    """Read Excel files into dictionary-based records.

    The reader uses pandas to load Excel sheets with all values treated as
    strings. Missing values are converted to empty strings so downstream
    pipeline logic can handle missing values consistently.
    """

    def read_sheet_as_records(self, file_path: str, sheet_name: str) -> list[dict]:
        """Read one Excel sheet and return its rows as records.

        Args:
            file_path: Path to the Excel workbook.
            sheet_name: Name of the sheet to read.

        Returns:
            A list of dictionaries. Each dictionary represents one row from the
            selected sheet.

        Notes:
            This method only reads the sheet. It does not validate,
            standardize, or transform the records.
        """
        path = Path(file_path)
        dataframe = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
        return dataframe.fillna("").to_dict(orient="records")

    def read_all_sheets_as_records(self, file_path: str) -> dict[str, list[dict]]:
        """Read all Excel sheets and return their rows as records.

        Args:
            file_path: Path to the Excel workbook.

        Returns:
            A dictionary where each key is a sheet name and each value is a list
            of row dictionaries from that sheet.

        Notes:
            This method is useful when the workbook contains multiple related
            sheets that must be ingested together.
        """
        path = Path(file_path)
        sheets = pd.read_excel(path, sheet_name=None, dtype=str)

        return {
            sheet_name: dataframe.fillna("").to_dict(orient="records")
            for sheet_name, dataframe in sheets.items()
        }