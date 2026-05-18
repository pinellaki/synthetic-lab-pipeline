from datetime import datetime

from src.schemas.ingestion_metadata import IngestionMetadata
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.validation.sample_submission_validator import SampleSubmissionValidator


def create_sample_submission(
    sample_id: str | None = "SMP-2026-00042",
    subject_id: str | None = "SUBJ-0001",
    intake_temperature_c: str | None = "4.2",
) -> SampleSubmissionRaw:
    return SampleSubmissionRaw(
        sample_id=sample_id,
        subject_id=subject_id,
        collection_site="SITE-001",
        sample_type="blood",
        collection_datetime="2026-01-30 01:00",
        received_datetime="2026-01-30 05:00",
        priority="routine",
        consent_recorded="yes",
        intake_temperature_c=intake_temperature_c,
        operator_notes=None,
        metadata=IngestionMetadata(
            source_file="sample_submissions.csv",
            source_row=1,
            run_id="test-run",
            ingested_at=datetime(2026, 1, 30, 6, 0),
        ),
    )


def test_missing_sample_id_is_invalid() -> None:
    validator = SampleSubmissionValidator()
    sample_submission = create_sample_submission(sample_id=None)

    result = validator.validate_required_sample_id(sample_submission)

    assert result.is_valid is False
    assert result.rule_id == "S1"
    assert result.action == "reject"


def test_present_sample_id_is_valid() -> None:
    validator = SampleSubmissionValidator()
    sample_submission = create_sample_submission(sample_id="SMP-2026-00042")

    result = validator.validate_required_sample_id(sample_submission)

    assert result.is_valid is True


def test_missing_subject_id_is_invalid() -> None:
    validator = SampleSubmissionValidator()
    sample_submission = create_sample_submission(subject_id=None)

    result = validator.validate_required_subject_id(sample_submission)

    assert result.is_valid is False
    assert result.rule_id == "S4"
    assert result.action == "review"


def test_collection_after_received_is_invalid() -> None:
    validator = SampleSubmissionValidator()

    result = validator.validate_collection_before_received(
        collection_datetime=datetime(2026, 1, 30, 10, 0),
        received_datetime=datetime(2026, 1, 30, 8, 0),
    )

    assert result.is_valid is False
    assert result.rule_id == "S8"


def test_collection_before_received_is_valid() -> None:
    validator = SampleSubmissionValidator()

    result = validator.validate_collection_before_received(
        collection_datetime=datetime(2026, 1, 30, 8, 0),
        received_datetime=datetime(2026, 1, 30, 10, 0),
    )

    assert result.is_valid is True


def test_non_numeric_temperature_is_invalid() -> None:
    validator = SampleSubmissionValidator()
    sample_submission = create_sample_submission(intake_temperature_c="abc")

    result = validator.validate_temperature_is_numeric(
        sample_submission.intake_temperature_c
    )

    assert result.is_valid is False
    assert result.rule_id == "S10"
    assert result.action == "review"


def test_numeric_temperature_is_valid() -> None:
    validator = SampleSubmissionValidator()
    sample_submission = create_sample_submission(intake_temperature_c="4.2")

    result = validator.validate_temperature_is_numeric(
        sample_submission.intake_temperature_c
    )

    assert result.is_valid is True