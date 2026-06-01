"""Validation rules for assay result records.

This module contains the AssayResultValidator class.

The validator checks raw assay result records before they are accepted into the
pipeline or loaded into the database. Each validation method returns a
ValidationResult object that explains whether a specific rule passed or failed.
"""

from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.validation_result import ValidationResult


class AssayResultValidator:
    """Validate assay result records.

    This validator focuses on required assay result fields and numeric result
    value rules.

    Each method validates one business rule and returns a ValidationResult.
    """

    def validate_required_result_id(
        self,
        assay_result: AssayResultRaw,
    ) -> ValidationResult:
        """Validate that the assay result has a result ID.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if result_id is present.
            An invalid ValidationResult if result_id is missing or empty.

        Rule:
            R1 — result_id is required.

        Action:
            Reject the record if the rule fails.
        """
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
        """Validate that the assay result belongs to a sample.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if sample_id is present.
            An invalid ValidationResult if sample_id is missing or empty.

        Rule:
            R2 — sample_id is required.

        Action:
            Reject the record if the rule fails.
        """
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
        """Validate that the assay result has an analyte code.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if analyte_code is present.
            An invalid ValidationResult if analyte_code is missing or empty.

        Rule:
            R4 — analyte_code is required.

        Action:
            Reject the record if the rule fails.
        """
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
        """Validate that result_value_raw is present and numeric.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if result_value_raw can be converted to a
            number. An invalid ValidationResult if the value is missing, empty,
            or not numeric.

        Rule:
            R6 — result_value is required and must be numeric.

        Action:
            Reject the record if the rule fails.

        Notes:
            Commas are converted to dots before numeric parsing so values such
            as ``"12,5"`` can be interpreted as ``12.5``.
        """
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
        """Validate that result_value_raw is not negative.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if the result value is numeric and greater
            than or equal to zero. An invalid ValidationResult if the value is
            missing, not numeric, or negative.

        Rule:
            R7 — result_value must be non-negative.

        Action:
            Reject the record if the rule fails.

        Notes:
            This method parses the raw value again because it is designed as an
            independent validation rule.
        """
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
        """Validate that the assay result has a unit.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A valid ValidationResult if unit_raw is present.
            An invalid ValidationResult if unit_raw is missing or empty.

        Rule:
            R9 — unit is required.

        Action:
            Send the record to review if the rule fails.
        """
        if assay_result.unit_raw is None or assay_result.unit_raw.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="R9",
                severity="high",
                message="unit is required.",
                action="review",
            )

        return ValidationResult(is_valid=True)