"""M8 sample data schema conversion test.

This script reads fake M8 example CSV files and converts the raw dictionaries
into Pydantic schema objects.

It does not use real company data.
It does not load data into PostgreSQL.
It only verifies that fake input rows can become structured pipeline objects.
"""

from datetime import UTC, datetime
from pathlib import Path

from src.ingestion.csv_reader import CsvReader
from src.schemas.assay_result_raw import AssayResultRaw
from src.schemas.ingestion_metadata import IngestionMetadata
from src.schemas.sample_submission_raw import SampleSubmissionRaw
from src.schemas.shipment_raw import ShipmentRaw
from src.schemas.workflow_event_raw import WorkflowEventRaw


DATA_DIR = Path("data/raw/examples")
RUN_ID = "M8_FAKE_DATA_SCHEMA_TEST"


def build_metadata(
    source_file: str,
    source_row: int,
) -> IngestionMetadata:
    """Create ingestion metadata for one fake source row.

    Args:
        source_file: Name of the fake input file.
        source_row: Row number from the fake input file.

    Returns:
        IngestionMetadata object for traceability.
    """
    return IngestionMetadata(
        source_file=source_file,
        source_row=source_row,
        run_id=RUN_ID,
        ingested_at=datetime.now(UTC),
    )


def build_sample_submissions() -> list[SampleSubmissionRaw]:
    """Read fake sample submissions and convert them to schema objects."""
    csv_reader = CsvReader()
    rows = csv_reader.read_rows_as_dicts(str(DATA_DIR / "sample_submissions.csv"))

    return [
        SampleSubmissionRaw(
            sample_id=row.get("sample_id"),
            subject_id=row.get("subject_id"),
            collection_site=row.get("collection_site"),
            sample_type=row.get("sample_type"),
            collection_datetime=row.get("collection_datetime"),
            received_datetime=row.get("received_datetime"),
            priority=row.get("priority"),
            consent_recorded=row.get("consent_recorded"),
            intake_temperature_c=row.get("intake_temperature_c"),
            operator_notes=row.get("operator_notes"),
            metadata=build_metadata("sample_submissions.csv", index),
        )
        for index, row in enumerate(rows, start=2)
    ]


def build_assay_results() -> list[AssayResultRaw]:
    """Read fake assay results and convert them to schema objects."""
    csv_reader = CsvReader()
    rows = csv_reader.read_rows_as_dicts(str(DATA_DIR / "assay_results.csv"))

    return [
        AssayResultRaw(
            result_id=row.get("result_id"),
            sample_id=row.get("sample_id"),
            analyte_code=row.get("analyte_code"),
            result_value_raw=row.get("result_value_raw"),
            unit_raw=row.get("unit_raw"),
            run_datetime_raw=row.get("run_datetime_raw"),
            instrument_id=row.get("instrument_id"),
            analyst=row.get("analyst"),
            qc_status=row.get("qc_status"),
            review_status=row.get("review_status"),
            approved_at_raw=row.get("approved_at_raw"),
            version=row.get("version"),
            is_current_raw=row.get("is_current_raw"),
            deleted_at_raw=row.get("deleted_at_raw"),
            metadata=build_metadata("assay_results.csv", index),
        )
        for index, row in enumerate(rows, start=2)
    ]


def build_shipments() -> list[ShipmentRaw]:
    """Read fake shipments and convert them to schema objects."""
    csv_reader = CsvReader()
    rows = csv_reader.read_rows_as_dicts(str(DATA_DIR / "shipments.csv"))

    return [
        ShipmentRaw(
            shipment_id=row.get("shipment_id"),
            sample_id=row.get("sample_id"),
            courier=row.get("courier"),
            shipped_at_raw=row.get("shipped_at_raw"),
            received_at_raw=row.get("received_at_raw"),
            condition_temp_c_raw=row.get("condition_temp_c_raw"),
            status=row.get("status"),
            api_updated_at_raw=row.get("api_updated_at_raw"),
            metadata=build_metadata("shipments.csv", index),
        )
        for index, row in enumerate(rows, start=2)
    ]


def build_workflow_events() -> list[WorkflowEventRaw]:
    """Read fake workflow events and convert them to schema objects."""
    csv_reader = CsvReader()
    rows = csv_reader.read_rows_as_dicts(str(DATA_DIR / "workflow_events.csv"))

    return [
        WorkflowEventRaw(
            event_id=row.get("event_id"),
            sample_id=row.get("sample_id"),
            event_status=row.get("event_status"),
            event_timestamp_raw=row.get("event_timestamp_raw"),
            actor=row.get("actor"),
            message=row.get("message"),
            metadata=build_metadata("workflow_events.csv", index),
        )
        for index, row in enumerate(rows, start=2)
    ]


def main() -> None:
    """Build schema objects from all fake input files and print counts."""
    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()
    shipments = build_shipments()
    workflow_events = build_workflow_events()

    print("M8 sample data schema conversion test")
    print("=====================================")
    print(f"SampleSubmissionRaw objects: {len(sample_submissions)}")
    print(f"AssayResultRaw objects: {len(assay_results)}")
    print(f"ShipmentRaw objects: {len(shipments)}")
    print(f"WorkflowEventRaw objects: {len(workflow_events)}")

    if len(sample_submissions) != 4:
        raise RuntimeError("Unexpected sample submission count.")

    if len(assay_results) != 5:
        raise RuntimeError("Unexpected assay result count.")

    if len(shipments) != 5:
        raise RuntimeError("Unexpected shipment count.")

    if len(workflow_events) != 6:
        raise RuntimeError("Unexpected workflow event count.")

    print("Schema conversion test passed.")


if __name__ == "__main__":
    main()