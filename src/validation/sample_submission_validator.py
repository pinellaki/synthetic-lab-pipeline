"""Validation rules for sample submission records.

This module contains the SampleSubmissionValidator class.

The validator checks cleaned sample submission records before they are accepted
into the pipeline or loaded into the database. Each validation method returns a
ValidationResult object that describes whether the check passed or failed.
"""

from datetime import datetime

from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.validation_result import ValidationResult


class SampleSubmissionValidator:
    """Validate sample submission records.

    This validator focuses on business rules related to sample submissions,
    such as required identifiers, date chronology, and numeric temperature
    values.

    Each method validates one rule and returns a ValidationResult.
    """

    def validate_required_sample_id(
        self,
        sample_submission: SampleSubmissionRaw,
    ) -> ValidationResult:
        """Validate that the sample submission has a sample ID.

        Args:
            sample_submission: Raw sample submission record to validate.

        Returns:
            A valid ValidationResult if sample_id is present.
            An invalid ValidationResult if sample_id is missing or empty.

        Rule:
            S1 — sample_id is required.

        Action:
            Reject the record if the rule fails.
        """
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
        """Validate that the sample submission has a subject ID.

        Args:
            sample_submission: Raw sample submission record to validate.

        Returns:
            A valid ValidationResult if subject_id is present.
            An invalid ValidationResult if subject_id is missing or empty.

        Rule:
            S4 — subject_id is required.

        Action:
            Send the record to review if the rule fails.
        """
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
        """Validate that collection_datetime is not after received_datetime.

        Args:
            collection_datetime: Parsed sample collection datetime.
            received_datetime: Parsed sample received datetime.

        Returns:
            A valid ValidationResult if the dates are present and collection is
            before or equal to received. Returns an invalid ValidationResult if
            either datetime is missing or if collection is after received.

        Rule:
            S8 — collection_datetime must be before or equal to received_datetime.

        Action:
            Send the record to review if the rule fails.
        """
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
        """Validate that intake temperature is numeric when provided.

        Args:
            raw_temperature: Raw intake temperature value from the source file.

        Returns:
            A valid ValidationResult if the value is missing, empty, or can be
            converted to a float. Returns an invalid ValidationResult if the
            value is present but not numeric.

        Rule:
            S10 — intake_temperature_c must be numeric.

        Action:
            Send the record to review if the rule fails.
        """
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