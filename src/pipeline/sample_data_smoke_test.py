"""M8 sample data smoke test.

This script checks that the M8 fake example input files can be read by the
existing ingestion readers.

It does not use real company data.
It does not load data into PostgreSQL.
It only verifies that the local fake files can be read successfully.
"""

from pathlib import Path

from src.ingestion.csv_reader import CsvReader


DATA_DIR = Path("data/raw/examples")


def main() -> None:
    """Read the M8 fake input files and print record counts."""
    csv_reader = CsvReader()

    sample_submissions = csv_reader.read_rows_as_dicts(
        str(DATA_DIR / "sample_submissions.csv")
    )
    assay_results = csv_reader.read_rows_as_dicts(
        str(DATA_DIR / "assay_results.csv")
    )
    shipments = csv_reader.read_rows_as_dicts(
        str(DATA_DIR / "shipments.csv")
    )
    workflow_events = csv_reader.read_rows_as_dicts(
        str(DATA_DIR / "workflow_events.csv")
    )

    actual_counts = {
        "sample_submissions": len(sample_submissions),
        "assay_results": len(assay_results),
        "shipments": len(shipments),
        "workflow_events": len(workflow_events),
    }

    expected_counts = {
        "sample_submissions": 4,
        "assay_results": 5,
        "shipments": 5,
        "workflow_events": 6,
    }

    print("M8 sample data smoke test")
    print("=========================")

    for name, count in actual_counts.items():
        print(f"{name}: {count} records")

    if actual_counts != expected_counts:
        raise RuntimeError(
            f"Unexpected record counts. Expected {expected_counts}, got {actual_counts}"
        )

    print("Smoke test passed.")


if __name__ == "__main__":
    main()