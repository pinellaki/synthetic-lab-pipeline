from datetime import datetime

from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.validation_result import ValidationResult


class SampleSubmissionValidator:
    def validate_required_sample_id(
        self,
        sample_submission: SampleSubmissionRaw,
    ) -> ValidationResult:
        if sample_submission.sample_id is None or sample_submission.sample_id.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="S1",
                severity="critical",
                message="sample_id is required.",
                action="reject",
            )

        return ValidationResult(is_valid=True)

    def validate_required_subject_id(
        self,
        sample_submission: SampleSubmissionRaw,
    ) -> ValidationResult:
        if sample_submission.subject_id is None or sample_submission.subject_id.strip() == "":
            return ValidationResult(
                is_valid=False,
                rule_id="S4",
                severity="high",
                message="subject_id is required.",
                action="review",
            )

        return ValidationResult(is_valid=True)

    def validate_collection_before_received(
        self,
        collection_datetime: datetime | None,
        received_datetime: datetime | None,
    ) -> ValidationResult:
        if collection_datetime is None or received_datetime is None:
            return ValidationResult(
                is_valid=False,
                rule_id="S8",
                severity="high",
                message="collection_datetime and received_datetime must be parseable.",
                action="review",
            )

        if collection_datetime > received_datetime:
            return ValidationResult(
                is_valid=False,
                rule_id="S8",
                severity="high",
                message="collection_datetime cannot be after received_datetime.",
                action="review",
            )

        return ValidationResult(is_valid=True)

    def validate_temperature_is_numeric(
        self,
        raw_temperature: str | None,
    ) -> ValidationResult:
        if raw_temperature is None or raw_temperature.strip() == "":
            return ValidationResult(is_valid=True)

        try:
            float(raw_temperature)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                rule_id="S10",
                severity="high",
                message="intake_temperature_c must be numeric.",
                action="review",
            )

        return ValidationResult(is_valid=True)