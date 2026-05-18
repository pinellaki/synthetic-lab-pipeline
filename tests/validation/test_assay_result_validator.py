from datetime import datetime

from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.ingestion_metadata import IngestionMetadata
from src.validation.assay_result_validator import AssayResultValidator


def create_assay_result(
    result_id: str | None = "RES-000001",
    sample_id: str | None = "SMP-2026-00042",
    analyte_code: str | None = "ALT",
    result_value_raw: str | None = "25.51",
    unit_raw: str | None = "U/L",
) -> AssayResultRaw:
    return AssayResultRaw(
        result_id=result_id,
        sample_id=sample_id,
        analyte_code=analyte_code,
        result_value_raw=result_value_raw,
        unit_raw=unit_raw,
        run_datetime_raw="2026-01-30 10:00",
        instrument_id="INST-001",
        analyst="analyst_001",
        qc_status="PASS",
        review_status="APPROVED",
        approved_at_raw="2026-01-30 11:00",
        version="1",
        is_current_raw="true",
        deleted_at_raw=None,
        metadata=IngestionMetadata(
            source_file="assay_results.csv",
            source_row=1,
            run_id="test-run",
            ingested_at=datetime(2026, 1, 30, 12, 0),
        ),
    )


def test_missing_result_id_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_id=None)

    result = validator.validate_required_result_id(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R1"
    assert result.action == "reject"


def test_present_result_id_is_valid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_id="RES-000001")

    result = validator.validate_required_result_id(assay_result)

    assert result.is_valid is True


def test_missing_sample_id_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(sample_id=None)

    result = validator.validate_required_sample_id(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R2"
    assert result.action == "reject"


def test_missing_analyte_code_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(analyte_code=None)

    result = validator.validate_required_analyte_code(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R4"
    assert result.action == "reject"


def test_non_numeric_result_value_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_value_raw="abc")

    result = validator.validate_result_value_is_numeric(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R6"
    assert result.action == "reject"


def test_decimal_comma_result_value_is_valid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_value_raw="25,51")

    result = validator.validate_result_value_is_numeric(assay_result)

    assert result.is_valid is True


def test_negative_result_value_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_value_raw="-4.2")

    result = validator.validate_result_value_is_non_negative(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R7"
    assert result.action == "reject"


def test_positive_result_value_is_valid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(result_value_raw="25.51")

    result = validator.validate_result_value_is_non_negative(assay_result)

    assert result.is_valid is True


def test_missing_unit_is_invalid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(unit_raw=None)

    result = validator.validate_required_unit(assay_result)

    assert result.is_valid is False
    assert result.rule_id == "R9"
    assert result.action == "review"


def test_present_unit_is_valid() -> None:
    validator = AssayResultValidator()
    assay_result = create_assay_result(unit_raw="U/L")

    result = validator.validate_required_unit(assay_result)

    assert result.is_valid is True