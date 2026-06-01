"""PDF report ingestion utilities.

This module defines the PdfReportReader class.

The PdfReportReader extracts text from PDF report files so later pipeline
steps can parse or validate the report content.
"""

from pathlib import Path


class PdfReportReader:
    """Extract text content from PDF report files.

    This reader uses ``pypdf`` to read PDF pages and collect their extracted
    text into one string.

    The reader only extracts text. It does not parse, validate, standardize,
    or structure the report content.
    """

    def extract_text(self, file_path: str) -> str:
        """Extract text from all pages of a PDF report.

        Args:
            file_path: Path to the PDF report file.

        Returns:
            The extracted text from all PDF pages, joined with newline
            characters.

        Raises:
            ImportError: If the ``pypdf`` package is not installed.

        Notes:
            Some PDFs may contain scanned images instead of selectable text.
            In those cases, ``pypdf`` may return empty text because OCR is not
            performed by this method.
        """
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise ImportError(
                "pypdf is required to extract text from PDF reports."
            ) from error

        path = Path(file_path)
        reader = PdfReader(str(path))

        page_texts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_texts.append(page_text)

        return "\n".join(page_texts)