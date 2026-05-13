from src.ingestion.csv_reader import CsvReader
from src.ingestion.excel_reader import ExcelReader
from src.ingestion.json_page_reader import JsonPageReader
from src.ingestion.pdf_report_reader import PdfReportReader
from src.ingestion.text_report_reader import TextReportReader


class IngestionService:
    def __init__(
        self,
        csv_reader: CsvReader,
        excel_reader: ExcelReader,
        json_page_reader: JsonPageReader,
        text_report_reader: TextReportReader,
        pdf_report_reader: PdfReportReader,
    ) -> None:
        self.csv_reader = csv_reader
        self.excel_reader = excel_reader
        self.json_page_reader = json_page_reader
        self.text_report_reader = text_report_reader
        self.pdf_report_reader = pdf_report_reader

    def ingest_csv(self, file_path: str) -> list[dict[str, str]]:
        return self.csv_reader.read_rows_as_dicts(file_path)

    def ingest_excel_workbook(self, file_path: str) -> dict[str, list[dict]]:
        return self.excel_reader.read_all_sheets_as_records(file_path)

    def ingest_json_pages(self, first_page_path: str) -> list[dict]:
        return self.json_page_reader.read_paginated_records(first_page_path)

    def ingest_text_report(self, file_path: str) -> str:
        return self.text_report_reader.read_text(file_path)

    def ingest_pdf_report(self, file_path: str) -> str:
        return self.pdf_report_reader.extract_text(file_path)