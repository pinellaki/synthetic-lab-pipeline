"""Ingestion service for coordinating file readers.

This module defines the IngestionService class.

The service provides a single entry point for reading different raw data
sources, such as CSV files, Excel workbooks, paginated JSON files, text reports,
and PDF reports.
"""

from src.ingestion.csv_reader import CsvReader
from src.ingestion.excel_reader import ExcelReader
from src.ingestion.json_page_reader import JsonPageReader
from src.ingestion.pdf_report_reader import PdfReportReader
from src.ingestion.text_report_reader import TextReportReader


class IngestionService:
    """Coordinate ingestion readers for different source file types.

    The service receives specialized reader classes through its constructor and
    delegates each ingestion operation to the correct reader.

    This keeps file-specific reading logic separate from the higher-level
    ingestion workflow.
    """

    def __init__(
        self,
        csv_reader: CsvReader,
        excel_reader: ExcelReader,
        json_page_reader: JsonPageReader,
        text_report_reader: TextReportReader,
        pdf_report_reader: PdfReportReader,
    ) -> None:
        """Initialize the ingestion service.

        Args:
            csv_reader: Reader used for CSV files.
            excel_reader: Reader used for Excel workbooks.
            json_page_reader: Reader used for paginated JSON files.
            text_report_reader: Reader used for plain text reports.
            pdf_report_reader: Reader used for PDF reports.
        """
        self.csv_reader = csv_reader
        self.excel_reader = excel_reader
        self.json_page_reader = json_page_reader
        self.text_report_reader = text_report_reader
        self.pdf_report_reader = pdf_report_reader

    def ingest_csv(self, file_path: str) -> list[dict[str, str]]:
        """Read a CSV file as row dictionaries.

        Args:
            file_path: Path to the CSV file.

        Returns:
            A list of dictionaries, where each dictionary represents one CSV
            row.
        """
        return self.csv_reader.read_rows_as_dicts(file_path)

    def ingest_excel_workbook(self, file_path: str) -> dict[str, list[dict]]:
        """Read all sheets from an Excel workbook.

        Args:
            file_path: Path to the Excel workbook.

        Returns:
            A dictionary where each key is a sheet name and each value is a
            list of row dictionaries from that sheet.
        """
        return self.excel_reader.read_all_sheets_as_records(file_path)

    def ingest_json_pages(self, first_page_path: str) -> list[dict]:
        """Read all records from a paginated JSON sequence.

        Args:
            first_page_path: Path to the first JSON page.

        Returns:
            A list of dictionaries collected from all linked JSON pages.
        """
        return self.json_page_reader.read_paginated_records(first_page_path)

    def ingest_text_report(self, file_path: str) -> str:
        """Read a plain text report.

        Args:
            file_path: Path to the text report file.

        Returns:
            Full text content of the report.
        """
        return self.text_report_reader.read_text(file_path)

    def ingest_pdf_report(self, file_path: str) -> str:
        """Extract text from a PDF report.

        Args:
            file_path: Path to the PDF report file.

        Returns:
            Extracted text from the PDF report.
        """
        return self.pdf_report_reader.extract_text(file_path)