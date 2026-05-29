"""Utilities for standardizing sample identifiers.

This module contains the SampleIdStandardizer class, which normalizes
raw sample identifiers before validation, quality checks, or database loading.
"""


class SampleIdStandardizer:
    """Normalize raw sample identifiers into a consistent format.

    The standardizer applies simple cleaning rules to sample identifiers:

    - remove leading and trailing whitespace
    - convert the value to uppercase
    - treat empty strings as missing values

    This keeps sample identifiers consistent before they are validated or
    compared across files.
    """

    def standardize(self, sample_id: str | None) -> str | None:
        """Return a cleaned sample identifier.

        Args:
            sample_id: Raw sample identifier from a source file. The value
                can be a string or None.

        Returns:
            The cleaned sample identifier in uppercase. Returns None if the
            input is None or if the value becomes empty after trimming
            whitespace.

        Examples:
            >>> standardizer = SampleIdStandardizer()
            >>> standardizer.standardize(" smp-001 ")
            'SMP-001'
            >>> standardizer.standardize("")
            None
        """
        if sample_id is None:
            return None

        cleaned_sample_id = sample_id.strip().upper()

        if cleaned_sample_id == "":
            return None

        return cleaned_sample_id