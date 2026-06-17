"""Load controlled reference data into PostgreSQL.

This module inserts the sites, analytes, and validation-rule definitions needed
before business records can be loaded.

All SQL values are passed as parameters. Credentials are not handled here;
the database connection is created separately.
"""

from typing import Any

from src.database.postgres_reference_data import (
    ANALYTE_ROWS,
    SITE_ROWS,
    VALIDATION_RULE_ROWS,
)


def load_site_rows(cursor: Any) -> int:
    """Insert or update collection-site reference rows."""
    parameters = [
        (
            row["site_code"],
            row["site_name"],
            row["country"],
            row["site_type"],
            row["source_file"],
            row["source_row"],
        )
        for row in SITE_ROWS
    ]

    cursor.executemany(
        """
        INSERT INTO dim_site (
            site_code,
            site_name,
            country,
            site_type,
            source_file,
            source_row
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (site_code) DO UPDATE
        SET
            site_name = EXCLUDED.site_name,
            country = EXCLUDED.country,
            site_type = EXCLUDED.site_type,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row
        """,
        parameters,
    )

    return len(parameters)


def load_analyte_rows(cursor: Any) -> int:
    """Insert or update analyte reference rows."""
    parameters = [
        (
            row["analyte_code"],
            row["analyte_name"],
            row["canonical_unit"],
            row["reference_low"],
            row["reference_high"],
            row["source_file"],
            row["source_row"],
        )
        for row in ANALYTE_ROWS
    ]

    cursor.executemany(
        """
        INSERT INTO dim_analyte (
            analyte_code,
            analyte_name,
            canonical_unit,
            reference_low,
            reference_high,
            source_file,
            source_row
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (analyte_code) DO UPDATE
        SET
            analyte_name = EXCLUDED.analyte_name,
            canonical_unit = EXCLUDED.canonical_unit,
            reference_low = EXCLUDED.reference_low,
            reference_high = EXCLUDED.reference_high,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row
        """,
        parameters,
    )

    return len(parameters)


def load_validation_rule_rows(cursor: Any) -> int:
    """Insert or update validation-rule reference rows."""
    parameters = [
        (
            row["rule_id"],
            row["target_table"],
            row["target_field"],
            row["severity"],
            row["action"],
            row["description"],
        )
        for row in VALIDATION_RULE_ROWS
    ]

    cursor.executemany(
        """
        INSERT INTO validation_rule (
            rule_id,
            target_table,
            target_field,
            severity,
            action,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (rule_id) DO UPDATE
        SET
            target_table = EXCLUDED.target_table,
            target_field = EXCLUDED.target_field,
            severity = EXCLUDED.severity,
            action = EXCLUDED.action,
            description = EXCLUDED.description
        """,
        parameters,
    )

    return len(parameters)


def load_reference_data(cursor: Any) -> dict[str, int]:
    """Load all reference tables in their required order."""
    return {
        "dim_site": load_site_rows(cursor),
        "dim_analyte": load_analyte_rows(cursor),
        "validation_rule": load_validation_rule_rows(cursor),
    }