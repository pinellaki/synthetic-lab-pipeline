"""Utilities for standardizing raw datetime values.

This module contains the DateStandardizer class, which converts raw datetime
strings from source files into Python datetime objects.

The input files may contain dates in different formats. This standardizer tries
a controlled list of accepted formats and returns the first successful parse.
"""

from datetime import datetime


class DateStandardizer:
    """Convert raw datetime strings into datetime objects.

    The standardizer supports multiple known datetime formats.

    Supported formats:

    - ``YYYY-MM-DD HH:MM``
    - ``DD/MM/YYYY HH:MM``
    - ``YYYY/MM/DD HH:MM``

    The standardizer applies these rules:

    - return None if the input is missing
    - remove leading and trailing whitespace
    - return None for empty strings
    - try each accepted datetime format in order
    - return the parsed datetime if one format matches
    - return None if no format matches

    This keeps datetime handling consistent before validation, database loading,
    and quality checks.
    """

    DATE_FORMATS = [
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    def standardize(self, raw_datetime: str | None) -> datetime | None:
        """Return a parsed datetime object from a raw datetime string.

        Args:
            raw_datetime: Raw datetime value from a source file. The value can
                be a string or None.

        Returns:
            A datetime object if the raw value matches one of the supported
            formats. Returns None if the input is missing, empty, or cannot be
            parsed.

        Examples:
            >>> standardizer = DateStandardizer()
            >>> standardizer.standardize("2026-05-20 14:30")
            datetime.datetime(2026, 5, 20, 14, 30)
            >>> standardizer.standardize("")
            None
            >>> standardizer.standardize("wrong-date")
            None
        """
        if raw_datetime is None:
            return None

        cleaned_datetime = raw_datetime.strip()

        if cleaned_datetime == "":
            return None

        for date_format in self.DATE_FORMATS:
            parsed_datetime = self._try_parse(cleaned_datetime, date_format)

            if parsed_datetime is not None:
                return parsed_datetime

        return None

    def _try_parse(self, raw_datetime: str, date_format: str) -> datetime | None:
        """Try to parse a datetime string using one specific format.

        Args:
            raw_datetime: Cleaned datetime string to parse.
            date_format: datetime format pattern used by ``datetime.strptime``.

        Returns:
            A datetime object if parsing succeeds. Returns None if the value
            does not match the provided format.

        Notes:
            This helper method catches ``ValueError`` so the main standardize
            method can safely try multiple formats without stopping the whole
            process.
        """
        try:
            return datetime.strptime(raw_datetime, date_format)
        except ValueError:
            return None