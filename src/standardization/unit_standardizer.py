"""Utilities for standardizing laboratory measurement units.

This module contains the UnitStandardizer class, which converts raw unit
values from source files into canonical units.

Laboratory data can contain the same unit written in different ways. For
example, "mg/dl", "mg_dl", "mg dl", and "mg_per_dl" should all become the
same canonical unit: "mg/dL".
"""


class UnitStandardizer:
    """Convert raw laboratory unit values into canonical unit values.

    The standardizer uses a mapping of accepted raw unit formats to one
    canonical representation.

    The standardizer applies these rules:

    - return None if the input is missing
    - remove leading and trailing whitespace
    - convert the unit to lowercase
    - return None for empty strings
    - return the canonical mapped unit if the cleaned value is recognized
    - return None for unknown units

    This helps avoid comparing or storing equivalent units in different
    formats.
    """

    UNIT_MAPPING = {
        "mg/dl": "mg/dL",
        "mg_dl": "mg/dL",
        "mg dl": "mg/dL",
        "mg_per_dl": "mg/dL",
        "mg per dl": "mg/dL",
        "mmol/l": "mmol/L",
        "mmol_l": "mmol/L",
        "mmol per l": "mmol/L",
        "u/l": "U/L",
        "units/l": "U/L",
        "unit/l": "U/L",
        "mg/l": "mg/L",
        "mg l": "mg/L",
    }

    def standardize(self, raw_unit: str | None) -> str | None:
        """Return the canonical unit for a raw unit value.

        Args:
            raw_unit: Raw unit value from a source file. The value can be a
                string or None.

        Returns:
            The canonical unit if the cleaned raw unit is recognized.
            Returns None if the input is missing, empty, or unknown.

        Examples:
            >>> standardizer = UnitStandardizer()
            >>> standardizer.standardize("MG/DL")
            'mg/dL'
            >>> standardizer.standardize("mg_per_dl")
            'mg/dL'
            >>> standardizer.standardize("unknown")
            None
        """
        if raw_unit is None:
            return None

        cleaned_unit = raw_unit.strip().lower()

        if cleaned_unit == "":
            return None

        return self.UNIT_MAPPING.get(cleaned_unit)