"""One-time PostgreSQL loader for the synthetic lab pipeline.

This module inserts the prepared M8 fake-data rows into the normalized
PostgreSQL schema.

The required load order is:

1. reference tables
2. samples
3. assay results
4. shipments
5. workflow events
6. validation results
7. rejected records

All values are passed through parameterized SQL queries.
The caller controls whether the transaction is committed or rolled back.
"""

from typing import Any

from src.database.postgres_audit_row_builder import (
    build_rejected_record_rows,
    build_validation_result_rows,
)
from src.database.postgres_reference_loader import load_reference_data
from src.database.postgres_row_builder import (
    build_valid_assay_result_rows,
    build_valid_sample_rows,
    build_valid_shipment_rows,
    build_valid_workflow_event_rows,
)


def load_sample_rows(cursor: Any) -> int:
    """Insert or update valid sample rows."""
    rows = build_valid_sample_rows()

    parameters = [
        (
            row["sample_id"],
            row["subject_id"],
            row["collection_site_code"],
            row["sample_type"],
            row["collection_datetime"],
            row["received_datetime"],
            row["priority"],
            row["consent_recorded"],
            row["intake_temperature_c"],
            row["operator_notes"],
            row["source_file"],
            row["source_row"],
            row["ingested_at"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO sample (
            sample_id,
            subject_id,
            collection_site_code,
            sample_type,
            collection_datetime,
            received_datetime,
            priority,
            consent_recorded,
            intake_temperature_c,
            operator_notes,
            source_file,
            source_row,
            ingested_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (sample_id) DO UPDATE
        SET
            subject_id = EXCLUDED.subject_id,
            collection_site_code = EXCLUDED.collection_site_code,
            sample_type = EXCLUDED.sample_type,
            collection_datetime = EXCLUDED.collection_datetime,
            received_datetime = EXCLUDED.received_datetime,
            priority = EXCLUDED.priority,
            consent_recorded = EXCLUDED.consent_recorded,
            intake_temperature_c = EXCLUDED.intake_temperature_c,
            operator_notes = EXCLUDED.operator_notes,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row,
            ingested_at = EXCLUDED.ingested_at
        """,
        parameters,
    )

    return len(parameters)


def load_assay_result_rows(cursor: Any) -> int:
    """Insert or update valid assay-result rows."""
    rows = build_valid_assay_result_rows()

    parameters = [
        (
            row["result_id"],
            row["sample_id"],
            row["analyte_code"],
            row["result_value"],
            row["unit"],
            row["run_datetime"],
            row["instrument_id"],
            row["analyst"],
            row["qc_status"],
            row["review_status"],
            row["approved_at"],
            row["version"],
            row["is_current"],
            row["deleted_at"],
            row["source_file"],
            row["source_row"],
            row["ingested_at"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO assay_result (
            result_id,
            sample_id,
            analyte_code,
            result_value,
            unit,
            run_datetime,
            instrument_id,
            analyst,
            qc_status,
            review_status,
            approved_at,
            version,
            is_current,
            deleted_at,
            source_file,
            source_row,
            ingested_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (result_id) DO UPDATE
        SET
            sample_id = EXCLUDED.sample_id,
            analyte_code = EXCLUDED.analyte_code,
            result_value = EXCLUDED.result_value,
            unit = EXCLUDED.unit,
            run_datetime = EXCLUDED.run_datetime,
            instrument_id = EXCLUDED.instrument_id,
            analyst = EXCLUDED.analyst,
            qc_status = EXCLUDED.qc_status,
            review_status = EXCLUDED.review_status,
            approved_at = EXCLUDED.approved_at,
            version = EXCLUDED.version,
            is_current = EXCLUDED.is_current,
            deleted_at = EXCLUDED.deleted_at,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row,
            ingested_at = EXCLUDED.ingested_at
        """,
        parameters,
    )

    return len(parameters)


def load_shipment_rows(cursor: Any) -> int:
    """Insert or update valid shipment rows."""
    rows = build_valid_shipment_rows()

    parameters = [
        (
            row["shipment_id"],
            row["sample_id"],
            row["courier"],
            row["shipped_at"],
            row["received_at"],
            row["condition_temp_c"],
            row["status"],
            row["api_updated_at"],
            row["source_file"],
            row["source_page"],
            row["source_record_index"],
            row["ingested_at"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO shipment (
            shipment_id,
            sample_id,
            courier,
            shipped_at,
            received_at,
            condition_temp_c,
            status,
            api_updated_at,
            source_file,
            source_page,
            source_record_index,
            ingested_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (shipment_id) DO UPDATE
        SET
            sample_id = EXCLUDED.sample_id,
            courier = EXCLUDED.courier,
            shipped_at = EXCLUDED.shipped_at,
            received_at = EXCLUDED.received_at,
            condition_temp_c = EXCLUDED.condition_temp_c,
            status = EXCLUDED.status,
            api_updated_at = EXCLUDED.api_updated_at,
            source_file = EXCLUDED.source_file,
            source_page = EXCLUDED.source_page,
            source_record_index = EXCLUDED.source_record_index,
            ingested_at = EXCLUDED.ingested_at
        """,
        parameters,
    )

    return len(parameters)


def load_workflow_event_rows(cursor: Any) -> int:
    """Insert or update valid workflow-event rows."""
    rows = build_valid_workflow_event_rows()

    parameters = [
        (
            row["event_id"],
            row["sample_id"],
            row["event_status"],
            row["event_timestamp"],
            row["actor"],
            row["message"],
            row["source_file"],
            row["source_row"],
            row["ingested_at"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO workflow_event (
            event_id,
            sample_id,
            event_status,
            event_timestamp,
            actor,
            message,
            source_file,
            source_row,
            ingested_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (event_id) DO UPDATE
        SET
            sample_id = EXCLUDED.sample_id,
            event_status = EXCLUDED.event_status,
            event_timestamp = EXCLUDED.event_timestamp,
            actor = EXCLUDED.actor,
            message = EXCLUDED.message,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row,
            ingested_at = EXCLUDED.ingested_at
        """,
        parameters,
    )

    return len(parameters)


def load_validation_result_rows(cursor: Any) -> int:
    """Insert or update all validation-result audit rows."""
    rows = build_validation_result_rows()

    parameters = [
        (
            row["validation_result_id"],
            row["rule_id"],
            row["source_table"],
            row["source_record_id"],
            row["source_field"],
            row["is_valid"],
            row["severity"],
            row["action"],
            row["message"],
            row["source_file"],
            row["source_row"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO validation_result (
            validation_result_id,
            rule_id,
            source_table,
            source_record_id,
            source_field,
            is_valid,
            severity,
            action,
            message,
            source_file,
            source_row
        )
        VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        ON CONFLICT (validation_result_id) DO UPDATE
        SET
            rule_id = EXCLUDED.rule_id,
            source_table = EXCLUDED.source_table,
            source_record_id = EXCLUDED.source_record_id,
            source_field = EXCLUDED.source_field,
            is_valid = EXCLUDED.is_valid,
            severity = EXCLUDED.severity,
            action = EXCLUDED.action,
            message = EXCLUDED.message,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row
        """,
        parameters,
    )

    return len(parameters)


def load_rejected_record_rows(cursor: Any) -> int:
    """Insert or update rejected-record audit rows."""
    rows = build_rejected_record_rows()

    parameters = [
        (
            row["rejected_record_id"],
            row["source_table"],
            row["source_record_id"],
            row["source_file"],
            row["source_row"],
            row["source_sheet"],
            row["source_page"],
            row["rule_id"],
            row["severity"],
            row["rejection_reason"],
            row["raw_payload"],
            row["run_id"],
            row["rejected_at"],
        )
        for row in rows
    ]

    cursor.executemany(
        """
        INSERT INTO rejected_record (
            rejected_record_id,
            source_table,
            source_record_id,
            source_file,
            source_row,
            source_sheet,
            source_page,
            rule_id,
            severity,
            rejection_reason,
            raw_payload,
            run_id,
            rejected_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (rejected_record_id) DO UPDATE
        SET
            source_table = EXCLUDED.source_table,
            source_record_id = EXCLUDED.source_record_id,
            source_file = EXCLUDED.source_file,
            source_row = EXCLUDED.source_row,
            source_sheet = EXCLUDED.source_sheet,
            source_page = EXCLUDED.source_page,
            rule_id = EXCLUDED.rule_id,
            severity = EXCLUDED.severity,
            rejection_reason = EXCLUDED.rejection_reason,
            raw_payload = EXCLUDED.raw_payload,
            run_id = EXCLUDED.run_id,
            rejected_at = EXCLUDED.rejected_at
        """,
        parameters,
    )

    return len(parameters)


def load_all_postgres_rows(cursor: Any) -> dict[str, int]:
    """Load the complete fake dataset in foreign-key-safe order."""
    counts = load_reference_data(cursor)

    counts.update(
        {
            "sample": load_sample_rows(cursor),
            "assay_result": load_assay_result_rows(cursor),
            "shipment": load_shipment_rows(cursor),
            "workflow_event": load_workflow_event_rows(cursor),
            "validation_result": load_validation_result_rows(cursor),
            "rejected_record": load_rejected_record_rows(cursor),
        }
    )

    return counts