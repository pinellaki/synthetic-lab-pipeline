from pathlib import Path

import pandas as pd


class ExcelReader:
    def read_sheet_as_records(self, file_path: str, sheet_name: str) -> list[dict]:
        path = Path(file_path)
        dataframe = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
        return dataframe.fillna("").to_dict(orient="records")

    def read_all_sheets_as_records(self, file_path: str) -> dict[str, list[dict]]:
        path = Path(file_path)
        sheets = pd.read_excel(path, sheet_name=None, dtype=str)

        return {
            sheet_name: dataframe.fillna("").to_dict(orient="records")
            for sheet_name, dataframe in sheets.items()
        }