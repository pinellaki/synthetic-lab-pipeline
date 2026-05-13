from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.validation_result import ValidationResult


class AssayResultValidator:
    def validate_required_result_id(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.result_id is None or assay_result.result_id.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R1",
                severity="critical",
                message="result_id is required.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_required_sample_id(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.sample_id is None or assay_result.sample_id.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R2",
                severity="critical",
                message="sample_id is required.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_required_analyte_code(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.analyte_code is None or assay_result.analyte_code.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R4",
                severity="critical",
                message="analyte_code is required.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_result_value_is_numeric(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.result_value_raw is None or assay_result.result_value_raw.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R6",
                severity="critical",
                message="result_value is required and must be numeric.",
                action="reject",
            )

        normalized_value = assay_result.result_value_raw.replace(",", ".")

        try:
            float(normalized_value)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                rule_id="R6",
                severity="critical",
                message="result_value must be numeric.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_result_value_is_non_negative(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.result_value_raw is None or assay_result.result_value_raw.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R7",
                severity="critical",
                message="result_value is required.",
                action="reject",
            )

        normalized_value = assay_result.result_value_raw.replace(",", ".")

        try:
            numeric_value = float(normalized_value)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                rule_id="R7",
                severity="critical",
                message="result_value must be numeric before checking negativity.",
                action="reject",
            )

        if numeric_value < 0:
            return ValidationResult(
                is_valid=False,
                rule_id="R7",
                severity="critical",
                message="result_value must be non-negative.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_required_unit(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        if assay_result.unit_raw is None or assay_result.unit_raw.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R9",
                severity="high",
                message="unit is required.",
                action="review",
            )

        return ValidationResult(is_valid=True)