"""M8 sample data validation test.

This script reads fake M8 schema objects and applies the existing validators.

It does not use real company data.
It does not load data into PostgreSQL.
It only verifies that fake records can pass or fail validation as expected.
"""

from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
)
from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.validation_result import ValidationResult
from src.standardization.date_standardizer import DateStandardizer
from src.validation.assay_result_validator import AssayResultValidator
from src.validation.sample_submission_validator import SampleSubmissionValidator


def validate_sample_submission(
    sample_submission: SampleSubmissionRaw,
    validator: SampleSubmissionValidator,
    date_standardizer: DateStandardizer,
) -> list[ValidationResult]:
    """Validate one fake sample submission record.

    Args:
        sample_submission: Fake sample submission object to validate.
        validator: Validator used for sample submission checks.
        date_standardizer: Standardizer used to parse raw datetime fields.

    Returns:
        List of validation results for the sample submission.
    """
    collection_datetime = date_standardizer.standardize(
        sample_submission.collection_datetime
    )
    received_datetime = date_standardizer.standardize(
        sample_submission.received_datetime
    )

    return [
        validator.validate_required_sample_id(sample_submission),
        validator.validate_required_subject_id(sample_submission),
        validator.validate_collection_before_received(
            collection_datetime,
            received_datetime,
        ),
        validator.validate_temperature_is_numeric(
            sample_submission.intake_temperature_c
        ),
    ]


def validate_assay_result(
    assay_result: AssayResultRaw,
    validator: AssayResultValidator,
) -> list[ValidationResult]:
    """Validate one fake assay result record.

    Args:
        assay_result: Fake assay result object to validate.
        validator: Validator used for assay result checks.

    Returns:
        List of validation results for the assay result.
    """
    return [
        validator.validate_required_result_id(assay_result),
        validator.validate_required_sample_id(assay_result),
        validator.validate_required_analyte_code(assay_result),
        validator.validate_required_unit(assay_result),
        validator.validate_result_value_is_numeric(assay_result),
        validator.validate_result_value_is_non_negative(assay_result),
    ]


def count_invalid_results(validation_results: list[ValidationResult]) -> int:
    """Count failed validation results.

    Args:
        validation_results: Validation results to inspect.

    Returns:
        Number of invalid validation results.
    """
    return sum(1 for result in validation_results if not result.is_valid)


def get_failed_rule_ids(validation_results: list[ValidationResult]) -> list[str]:
    """Return rule IDs for failed validation results.

    Args:
        validation_results: Validation results to inspect.

    Returns:
        List of rule IDs for failed validations.
    """
    return [
        result.rule_id or "UNKNOWN"
        for result in validation_results
        if not result.is_valid
    ]


def main() -> None:
    """Validate fake sample and assay data and print validation results."""
    sample_validator = SampleSubmissionValidator()
    assay_validator = AssayResultValidator()
    date_standardizer = DateStandardizer()

    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()

    sample_validation_results: list[ValidationResult] = []
    assay_validation_results: list[ValidationResult] = []

    for sample_submission in sample_submissions:
        sample_validation_results.extend(
            validate_sample_submission(
                sample_submission=sample_submission,
                validator=sample_validator,
                date_standardizer=date_standardizer,
            )
        )

    for assay_result in assay_results:
        assay_validation_results.extend(
            validate_assay_result(
                assay_result=assay_result,
                validator=assay_validator,
            )
        )

    sample_invalid_count = count_invalid_results(sample_validation_results)
    assay_invalid_count = count_invalid_results(assay_validation_results)

    sample_failed_rules = get_failed_rule_ids(sample_validation_results)
    assay_failed_rules = get_failed_rule_ids(assay_validation_results)

    print("M8 sample data validation test")
    print("==============================")
    print(f"Sample validation results: {len(sample_validation_results)}")
    print(f"Sample invalid results: {sample_invalid_count}")
    print(f"Sample failed rule IDs: {sample_failed_rules}")
    print(f"Assay validation results: {len(assay_validation_results)}")
    print(f"Assay invalid results: {assay_invalid_count}")
    print(f"Assay failed rule IDs: {assay_failed_rules}")

    expected_sample_invalid_count = 3
    expected_assay_invalid_count = 4

    expected_sample_failed_rules = ["S1", "S4", "S10"]
    expected_assay_failed_rules = ["R7", "R6", "R7", "R1"]

    if sample_invalid_count != expected_sample_invalid_count:
        raise RuntimeError(
            "Unexpected sample invalid count. "
            f"Expected {expected_sample_invalid_count}, got {sample_invalid_count}."
        )

    if assay_invalid_count != expected_assay_invalid_count:
        raise RuntimeError(
            "Unexpected assay invalid count. "
            f"Expected {expected_assay_invalid_count}, got {assay_invalid_count}."
        )

    if sample_failed_rules != expected_sample_failed_rules:
        raise RuntimeError(
            "Unexpected sample failed rules. "
            f"Expected {expected_sample_failed_rules}, got {sample_failed_rules}."
        )

    if assay_failed_rules != expected_assay_failed_rules:
        raise RuntimeError(
            "Unexpected assay failed rules. "
            f"Expected {expected_assay_failed_rules}, got {assay_failed_rules}."
        )

    print("Validation test passed.")


if __name__ == "__main__":
    main()