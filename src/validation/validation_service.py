"""Validation service for coordinating record validation.

This module contains the ValidationService class.

The service groups individual validation rules into higher-level validation
flows. It does not define the business rules itself. Instead, it calls the
specific validator classes and returns lists of ValidationResult objects.
"""

from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.validation_result import ValidationResult
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


class ValidationService:
    """Coordinate validation checks across pipeline record types.

    The service receives specialized validators through its constructor and
    uses them to validate sample submissions and assay results.

    This keeps orchestration separate from the individual validation rules.
    """

    def __init__(
        self,
        sample_submission_validator: SampleSubmissionValidator,
        assay_result_validator: AssayResultValidator,
    ) -> None:
        """Initialize the validation service.

        Args:
            sample_submission_validator: Validator used for sample submission
                records.
            assay_result_validator: Validator used for assay result records.
        """
        self.sample_submission_validator = sample_submission_validator
        self.assay_result_validator = assay_result_validator

    def validate_sample_submission_required_fields(
        self,
        sample_submission: SampleSubmissionRaw,
    ) -> list[ValidationResult]:
        """Validate required fields for a sample submission record.

        Args:
            sample_submission: Raw sample submission record to validate.

        Returns:
            A list of ValidationResult objects for required sample submission
            fields.

        Checks:
            - sample_id is required
            - subject_id is required
        """
        return [
            self.sample_submission_validator.validate_required_sample_id(
                sample_submission
            ),
            self.sample_submission_validator.validate_required_subject_id(
                sample_submission
            ),
        ]

    def validate_assay_result_required_fields(
        self,
        assay_result: AssayResultRaw,
    ) -> list[ValidationResult]:
        """Validate required fields for an assay result record.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A list of ValidationResult objects for required assay result fields.

        Checks:
            - result_id is required
            - sample_id is required
            - analyte_code is required
            - unit is required
        """
        return [
            self.assay_result_validator.validate_required_result_id(assay_result),
            self.assay_result_validator.validate_required_sample_id(assay_result),
            self.assay_result_validator.validate_required_analyte_code(assay_result),
            self.assay_result_validator.validate_required_unit(assay_result),
        ]

    def validate_assay_result_value(
        self,
        assay_result: AssayResultRaw,
    ) -> list[ValidationResult]:
        """Validate assay result value rules.

        Args:
            assay_result: Raw assay result record to validate.

        Returns:
            A list of ValidationResult objects for assay result value checks.

        Checks:
            - result_value is numeric
            - result_value is non-negative
        """
        return [
            self.assay_result_validator.validate_result_value_is_numeric(assay_result),
            self.assay_result_validator.validate_result_value_is_non_negative(
                assay_result
            ),
        ]