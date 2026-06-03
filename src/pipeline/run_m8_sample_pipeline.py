"""M8 end-to-end sample pipeline runner.

This script runs the M8 fake-data pipeline flow from ingestion to rejected
record output.

It does not use real company data.
It does not load data into PostgreSQL.

The script demonstrates that the pipeline components can work together:

- read fake input files
- convert rows into Pydantic schema objects
- standardize selected values
- validate sample and assay records
- create rejected records
- write rejected records to CSV
- print a final summary
"""

from src.pipeline.sample_data_rejection_test import build_rejected_records
from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
    build_shipments,
    build_workflow_events,
)
from src.pipeline.sample_data_standardization_test import main as run_standardization_test
from src.rejection.rejected_record_writer import RejectedRecordWriter


REJECTED_OUTPUT_FILE = "data/rejected/m8_rejected_records.csv"


def main() -> None:
    """Run the M8 fake-data pipeline and print a final summary."""
    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()
    shipments = build_shipments()
    workflow_events = build_workflow_events()

    print("M8 end-to-end sample pipeline")
    print("=============================")
    print(f"Sample submissions read: {len(sample_submissions)}")
    print(f"Assay results read: {len(assay_results)}")
    print(f"Shipments read: {len(shipments)}")
    print(f"Workflow events read: {len(workflow_events)}")

    run_standardization_test()

    rejected_records = build_rejected_records()

    rejected_record_writer = RejectedRecordWriter()
    rejected_record_writer.write_records(
        rejected_records=rejected_records,
        output_file_path=REJECTED_OUTPUT_FILE,
    )

    print("Final M8 pipeline summary")
    print("=========================")
    print(f"Rejected records written: {len(rejected_records)}")
    print(f"Rejected output file: {REJECTED_OUTPUT_FILE}")

    expected_rejected_count = 7

    if len(rejected_records) != expected_rejected_count:
        raise RuntimeError(
            "Unexpected rejected record count. "
            f"Expected {expected_rejected_count}, got {len(rejected_records)}."
        )

    print("M8 sample pipeline completed successfully.")


if __name__ == "__main__":
    main()