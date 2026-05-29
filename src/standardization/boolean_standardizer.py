"""Utilities for standardizing boolean values.

This module contains the BooleanStandardizer class, which converts raw
boolean-like values from source files into real Python booleans.

The standardizer is useful because raw input files may represent boolean
values in different ways, for example "yes", "y", "true", "1", "no", "false",
or "0".
"""

from src.core.pipeline_constants import PipelineConstants


class BooleanStandardizer:
    """Convert raw boolean-like values into True, False, or None.

    The standardizer applies simple cleaning rules:

    - remove leading and trailing whitespace
    - convert the value to lowercase
    - map known true values to True
    - map known false values to False
    - return None for missing, empty, or unknown values

    This makes boolean fields consistent before validation and database
    loading.
    """

    def standardize(self, raw_value: str | None) -> bool | None:
        """Return a standardized boolean value.

        Args:
            raw_value: Raw boolean-like value from a source file. The value
                can be a string or None.

        Returns:
            True if the cleaned value is recognized as a true value.
            False if the cleaned value is recognized as a false value.
            None if the input is missing, empty, or not recognized.

        Examples:
            >>> standardizer = BooleanStandardizer()
            >>> standardizer.standardize("YES")
            True
            >>> standardizer.standardize("no")
            False
            >>> standardizer.standardize("")
            None
        """
        if raw_value is None:
            return None

        cleaned_value = raw_value.strip().lower()

        if cleaned_value == "":
            return None

        if cleaned_value in PipelineConstants.BOOLEAN_TRUE_VALUES:
            return True

        if cleaned_value in PipelineConstants.BOOLEAN_FALSE_VALUES:
            return False

        return None