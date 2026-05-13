class UnitStandardizer:
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
        if raw_unit is None:
            return None

        cleaned_unit = raw_unit.strip().lower()

        if cleaned_unit == "":
            return None

        return self.UNIT_MAPPING.get(cleaned_unit)