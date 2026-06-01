"""Text report ingestion utilities.

This module defines the TextReportReader class.

The TextReportReader reads plain text report files and returns their full
content as a string. Later pipeline steps can parse, validate, or extract
structured values from the returned text.
"""

from pathlib import Path


class TextReportReader:
    """Read plain text report files.

    This reader is used for source files where the input is an unstructured or
    semi-structured text report.

    The reader only loads the text content. It does not parse, validate, or
    standardize the report.
    """

    def read_text(self, file_path: str) -> str:
        """Read a text file and return its content.

        Args:
            file_path: Path to the text report file.

        Returns:
            The full content of the text file as a string.

        Notes:
            The file is read using UTF-8 encoding.
        """
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8") as text_file:
            return text_file.read()