"""M8 sample data standardization test.

This script reads fake M8 schema objects and applies the existing
standardizers.

It does not use real company data.
It does not load data into PostgreSQL.
It only verifies that raw fake values can be standardized consistently.
"""

from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
    build_shipments,
    build_workflow_events,
)
from src.standardization.boolean_standardizer import BooleanStandardizer
from src.standardization.date_standardizer import DateStandardizer
from src.standardization.sample_id_standardizer import SampleIdStandardizer
from src.standardization.unit_standardizer import UnitStandardizer


def main() -> None:
    """Apply standardizers to fake M8 data and validate expected results."""
    sample_id_standardizer = SampleIdStandardizer()
    boolean_standardizer = BooleanStandardizer()
    date_standardizer = DateStandardizer()
    unit_standardizer = UnitStandardizer()

    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()
    shipments = build_shipments()
    workflow_events = build_workflow_events()

    standardized_sample_ids = [
        sample_id_standardizer.standardize(sample.sample_id)
        for sample in sample_submissions
    ]

    standardized_consent_values = [
        boolean_standardizer.standardize(sample.consent_recorded)
        for sample in sample_submissions
    ]

    standardized_collection_dates = [
        date_standardizer.standardize(sample.collection_datetime)
        for sample in sample_submissions
    ]

    standardized_assay_sample_ids = [
        sample_id_standardizer.standardize(result.sample_id)
        for result in assay_results
    ]

    standardized_units = [
        unit_standardizer.standardize(result.unit_raw)
        for result in assay_results
    ]

    standardized_current_flags = [
        boolean_standardizer.standardize(result.is_current_raw)
        for result in assay_results
    ]

    standardized_run_dates = [
        date_standardizer.standardize(result.run_datetime_raw)
        for result in assay_results
    ]

    standardized_shipment_sample_ids = [
        sample_id_standardizer.standardize(shipment.sample_id)
        for shipment in shipments
    ]

    standardized_shipped_dates = [
        date_standardizer.standardize(shipment.shipped_at_raw)
        for shipment in shipments
    ]

    standardized_workflow_sample_ids = [
        sample_id_standardizer.standardize(event.sample_id)
        for event in workflow_events
    ]

    standardized_workflow_dates = [
        date_standardizer.standardize(event.event_timestamp_raw)
        for event in workflow_events
    ]

    print("M8 sample data standardization test")
    print("===================================")

    print(f"Standardized sample IDs: {standardized_sample_ids}")
    print(f"Standardized consent values: {standardized_consent_values}")
    print(f"Standardized assay units: {standardized_units}")
    print(f"Standardized assay current flags: {standardized_current_flags}")

    if standardized_sample_ids[0] != "SMP-001":
        raise RuntimeError("Expected first sample_id to standardize to SMP-001.")

    if standardized_sample_ids[2] is not None:
        raise RuntimeError("Expected missing sample_id to standardize to None.")

    if standardized_consent_values[0] is not True:
        raise RuntimeError("Expected yes to standardize to True.")

    if standardized_consent_values[1] is not False:
        raise RuntimeError("Expected no to standardize to False.")

    if standardized_collection_dates[0] is None:
        raise RuntimeError("Expected first collection date to parse.")

    if standardized_collection_dates[1] is None:
        raise RuntimeError("Expected alternative collection date format to parse.")

    if standardized_assay_sample_ids[0] != "SMP-001":
        raise RuntimeError("Expected assay sample_id to standardize to SMP-001.")

    if standardized_units[0] != "mg/dL":
        raise RuntimeError("Expected mg_dl to standardize to mg/dL.")

    if standardized_units[2] != "U/L":
        raise RuntimeError("Expected U/L to standardize to U/L.")

    if standardized_current_flags[0] is not True:
        raise RuntimeError("Expected yes to standardize to True.")

    if standardized_current_flags[2] is not False:
        raise RuntimeError("Expected no to standardize to False.")

    if standardized_run_dates[0] is None:
        raise RuntimeError("Expected first assay run date to parse.")

    if standardized_shipment_sample_ids[0] != "SMP-001":
        raise RuntimeError("Expected shipment sample_id to standardize to SMP-001.")

    if standardized_shipped_dates[0] is None:
        raise RuntimeError("Expected shipment shipped_at date to parse.")

    if standardized_workflow_sample_ids[0] != "SMP-001":
        raise RuntimeError("Expected workflow sample_id to standardize to SMP-001.")

    if standardized_workflow_sample_ids[5] is not None:
        raise RuntimeError("Expected missing workflow sample_id to standardize to None.")

    if standardized_workflow_dates[0] is None:
        raise RuntimeError("Expected workflow timestamp to parse.")

    print("Standardization test passed.")


if __name__ == "__main__":
    main()