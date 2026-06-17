"""Execute the one-time PostgreSQL load.

This script loads the validated M8 fake data into the normalized PostgreSQL
schema exactly once.

Safety behavior:

- verifies that all target tables are empty before loading
- loads all rows inside one transaction
- verifies final database row counts
- commits only when every check passes
- rolls back if any step fails
- refuses to run again when the database is already populated
"""

from typing import Any

from psycopg import sql

from src.database.postgres_connection import create_postgres_connection
from src.database.postgres_one_time_loader import load_all_postgres_rows


EXPECTED_FINAL_COUNTS = {
    "dim_site": 3,
    "dim_analyte": 3,
    "validation_rule": 10,
    "sample": 2,
    "assay_result": 2,
    "shipment": 2,
    "workflow_event": 4,
    "validation_result": 46,
    "rejected_record": 7,
}


def count_table_rows(cursor: Any, table_name: str) -> int:
    """Return the number of rows currently stored in one table."""
    cursor.execute(
        sql.SQL("SELECT COUNT(*) FROM {}").format(
            sql.Identifier(table_name)
        )
    )

    result = cursor.fetchone()

    if result is None:
        raise RuntimeError(
            f"Could not read the row count for table {table_name}."
        )

    return result[0]


def get_database_counts(cursor: Any) -> dict[str, int]:
    """Return current row counts for every one-time-load table."""
    return {
        table_name: count_table_rows(cursor, table_name)
        for table_name in EXPECTED_FINAL_COUNTS
    }


def ensure_database_is_empty(
    current_counts: dict[str, int],
) -> None:
    """Stop the one-time load if any target table already contains rows."""
    populated_tables = {
        table_name: row_count
        for table_name, row_count in current_counts.items()
        if row_count != 0
    }

    if populated_tables:
        details = ", ".join(
            f"{table_name}={row_count}"
            for table_name, row_count in populated_tables.items()
        )

        raise RuntimeError(
            "One-time load stopped because the database is not empty. "
            f"Existing rows: {details}"
        )


def verify_final_counts(
    final_counts: dict[str, int],
) -> None:
    """Verify that PostgreSQL contains the expected rows before commit."""
    if final_counts != EXPECTED_FINAL_COUNTS:
        raise RuntimeError(
            "Loaded row counts do not match the expected result. "
            f"Expected {EXPECTED_FINAL_COUNTS}, got {final_counts}."
        )


def print_counts(
    title: str,
    counts: dict[str, int],
) -> None:
    """Print a readable database count summary."""
    print(title)

    for table_name, row_count in counts.items():
        print(f"{table_name}: {row_count}")


def main() -> None:
    """Run and commit the one-time PostgreSQL load."""
    connection = create_postgres_connection()

    try:
        with connection.cursor() as cursor:
            starting_counts = get_database_counts(cursor)

            print_counts(
                title="Database rows before load:",
                counts=starting_counts,
            )

            ensure_database_is_empty(starting_counts)

            print("")
            print("Starting one-time PostgreSQL load...")

            loader_counts = load_all_postgres_rows(cursor)
            final_counts = get_database_counts(cursor)

            print("")
            print_counts(
                title="Rows prepared by loader:",
                counts=loader_counts,
            )

            print("")
            print_counts(
                title="Database rows after load:",
                counts=final_counts,
            )

            verify_final_counts(final_counts)

        connection.commit()

        print("")
        print("One-time PostgreSQL load completed successfully.")
        print("Transaction committed. Data is now permanently stored.")

    except Exception:
        connection.rollback()

        print("")
        print("One-time PostgreSQL load failed.")
        print("Transaction rolled back. No partial load was saved.")

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()