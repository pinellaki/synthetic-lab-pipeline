from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.validation_result import ValidationResult
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


class ValidationService:
    def __init__(
        self,
        sample_submission_validator: SampleSubmissionValidator,
        assay_result_validator: AssayResultValidator,
    ) -> None:
        self.sample_submission_validator = sample_submission_validator
        self.assay_result_validator = assay_result_validator

    def validate_sample_submission_required_fields(
        self,
        sample_submission: SampleSubmissionRaw,
    ) -> list[ValidationResult]:
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
        return [
            self.assay_result_validator.validate_result_value_is_numeric(assay_result),
            self.assay_result_validator.validate_result_value_is_non_negative(
                assay_result
            ),
        ]