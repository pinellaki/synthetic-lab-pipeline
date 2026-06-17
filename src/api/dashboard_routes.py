"""FastAPI routes for the Synthetic Lab Pipeline governance dashboard.

The endpoints retrieve laboratory, validation, rejection, lineage, and
issue-resolution information from PostgreSQL.

Most routes are read-only. One PATCH endpoint allows a rejected-record issue
to be marked as open, corrected, resolved, or dismissed.
"""

from decimal import Decimal
from typing import Any

from fastapi import APIRouter, HTTPException
from psycopg.rows import dict_row

from src.api.dashboard_schemas import (
    DashboardDocumentationResponse,
    DashboardOverviewResponse,
    LabResultMetric,
    LineageStageMetric,
    RejectedRecordItem,
    RejectedRecordResolutionResponse,
    RejectedRecordResolutionUpdate,
    ResolutionStatusMetric,
    SampleSummaryItem,
    ValidationRuleMetric,
    ValidationSeverityMetric,
)
from src.database.postgres_connection import create_postgres_connection


router = APIRouter(
    prefix="/dashboard",
    tags=["Governance dashboard"],
)


def decimal_to_float(value: Decimal | None) -> float | None:
    """Convert PostgreSQL numeric values into JSON-compatible floats."""
    if value is None:
        return None

    return float(value)


def execute_query(
    query: str,
    parameters: tuple[Any, ...] | None = None,
) -> list[dict[str, Any]]:
    """Execute a PostgreSQL read query and return dictionary rows."""
    connection = create_postgres_connection()

    try:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(query, parameters)
            return list(cursor.fetchall())

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Could not read dashboard data from PostgreSQL.",
        ) from error

    finally:
        connection.close()


def update_rejected_record_resolution(
    rejected_record_id: str,
    update: RejectedRecordResolutionUpdate,
) -> dict[str, Any]:
    """Update and return one rejected-record resolution entry."""
    connection = create_postgres_connection()

    try:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE rejected_record
                SET
                    resolution_status = %s,
                    corrected_value = %s,
                    resolution_note = %s,
                    resolved_by = %s,
                    resolved_at = CASE
                        WHEN %s = 'open' THEN NULL
                        ELSE CURRENT_TIMESTAMP
                    END
                WHERE rejected_record_id = %s
                RETURNING
                    rejected_record_id,
                    resolution_status,
                    corrected_value,
                    resolution_note,
                    resolved_by,
                    resolved_at
                """,
                (
                    update.resolution_status,
                    update.corrected_value,
                    update.resolution_note,
                    update.resolved_by,
                    update.resolution_status,
                    rejected_record_id,
                ),
            )

            updated_row = cursor.fetchone()

            if updated_row is None:
                connection.rollback()

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Rejected record was not found: "
                        f"{rejected_record_id}"
                    ),
                )

        connection.commit()
        return dict(updated_row)

    except HTTPException:
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail="Could not update the rejected-record issue.",
        ) from error

    finally:
        connection.close()


@router.get(
    "/overview",
    response_model=DashboardOverviewResponse,
    summary="Return dashboard overview metrics",
)
def get_dashboard_overview() -> DashboardOverviewResponse:
    """Return high-level data, validation, and issue-status counters."""
    rows = execute_query(
        """
        SELECT
            (SELECT COUNT(*) FROM sample) AS samples,
            (SELECT COUNT(*) FROM assay_result) AS assay_results,
            (SELECT COUNT(*) FROM shipment) AS shipments,
            (SELECT COUNT(*) FROM workflow_event) AS workflow_events,
            (SELECT COUNT(*) FROM validation_result) AS validation_results,
            (
                SELECT COUNT(*)
                FROM validation_result
                WHERE is_valid IS TRUE
            ) AS passed_validations,
            (
                SELECT COUNT(*)
                FROM validation_result
                WHERE is_valid IS FALSE
            ) AS failed_validations,
            (SELECT COUNT(*) FROM rejected_record) AS rejected_records,
            (
                SELECT COUNT(*)
                FROM rejected_record
                WHERE resolution_status = 'open'
            ) AS open_issues,
            (
                SELECT COUNT(*)
                FROM rejected_record
                WHERE resolution_status IN (
                    'corrected',
                    'resolved',
                    'dismissed'
                )
            ) AS resolved_issues
        """
    )

    if not rows:
        raise HTTPException(
            status_code=500,
            detail="Dashboard overview query returned no result.",
        )

    row = rows[0]
    validation_results = int(row["validation_results"])
    passed_validations = int(row["passed_validations"])

    validation_pass_rate = (
        round((passed_validations / validation_results) * 100, 2)
        if validation_results > 0
        else 0.0
    )

    return DashboardOverviewResponse(
        samples=int(row["samples"]),
        assay_results=int(row["assay_results"]),
        shipments=int(row["shipments"]),
        workflow_events=int(row["workflow_events"]),
        validation_results=validation_results,
        passed_validations=passed_validations,
        failed_validations=int(row["failed_validations"]),
        rejected_records=int(row["rejected_records"]),
        open_issues=int(row["open_issues"]),
        resolved_issues=int(row["resolved_issues"]),
        validation_pass_rate=validation_pass_rate,
    )


@router.get(
    "/lab-results",
    response_model=list[LabResultMetric],
    summary="Return assay-result metrics by analyte",
)
def get_lab_result_metrics() -> list[LabResultMetric]:
    """Return result counts and numeric summaries grouped by analyte."""
    rows = execute_query(
        """
        SELECT
            da.analyte_code,
            da.analyte_name,
            da.canonical_unit,
            COUNT(ar.result_id) AS result_count,
            AVG(ar.result_value) AS average_value,
            MIN(ar.result_value) AS minimum_value,
            MAX(ar.result_value) AS maximum_value
        FROM dim_analyte da
        LEFT JOIN assay_result ar
            ON ar.analyte_code = da.analyte_code
        GROUP BY
            da.analyte_code,
            da.analyte_name,
            da.canonical_unit
        ORDER BY da.analyte_code
        """
    )

    return [
        LabResultMetric(
            analyte_code=row["analyte_code"],
            analyte_name=row["analyte_name"],
            canonical_unit=row["canonical_unit"],
            result_count=int(row["result_count"]),
            average_value=decimal_to_float(row["average_value"]),
            minimum_value=decimal_to_float(row["minimum_value"]),
            maximum_value=decimal_to_float(row["maximum_value"]),
        )
        for row in rows
    ]


@router.get(
    "/samples",
    response_model=list[SampleSummaryItem],
    summary="Return detailed sample summaries",
)
def get_sample_summaries() -> list[SampleSummaryItem]:
    """Return the existing PostgreSQL sample-quality summary view."""
    rows = execute_query(
        """
        SELECT
            sample_id,
            subject_id,
            collection_site_code,
            site_name,
            sample_type,
            priority,
            assay_result_count,
            shipment_count,
            workflow_event_count,
            has_retry_or_repeat_message
        FROM sample_quality_summary_view
        ORDER BY sample_id
        """
    )

    return [
        SampleSummaryItem(
            sample_id=row["sample_id"],
            subject_id=row["subject_id"],
            collection_site_code=row["collection_site_code"],
            site_name=row["site_name"],
            sample_type=row["sample_type"],
            priority=row["priority"],
            assay_result_count=int(row["assay_result_count"]),
            shipment_count=int(row["shipment_count"]),
            workflow_event_count=int(row["workflow_event_count"]),
            has_retry_or_repeat_message=bool(
                row["has_retry_or_repeat_message"]
            ),
        )
        for row in rows
    ]


@router.get(
    "/validation-rules",
    response_model=list[ValidationRuleMetric],
    summary="Return validation metrics by rule",
)
def get_validation_rule_metrics() -> list[ValidationRuleMetric]:
    """Return passed and failed validation counts for every rule."""
    rows = execute_query(
        """
        SELECT
            vrule.rule_id,
            vrule.description,
            vrule.severity,
            vrule.action,
            COUNT(vresult.validation_result_id) AS total_checks,
            COUNT(vresult.validation_result_id)
                FILTER (WHERE vresult.is_valid IS TRUE) AS passed_checks,
            COUNT(vresult.validation_result_id)
                FILTER (WHERE vresult.is_valid IS FALSE) AS failed_checks
        FROM validation_rule vrule
        LEFT JOIN validation_result vresult
            ON vresult.rule_id = vrule.rule_id
        GROUP BY
            vrule.rule_id,
            vrule.description,
            vrule.severity,
            vrule.action
        ORDER BY vrule.rule_id
        """
    )

    return [
        ValidationRuleMetric(
            rule_id=row["rule_id"],
            description=row["description"],
            severity=row["severity"],
            action=row["action"],
            total_checks=int(row["total_checks"]),
            passed_checks=int(row["passed_checks"]),
            failed_checks=int(row["failed_checks"]),
        )
        for row in rows
    ]


@router.get(
    "/validation-severity",
    response_model=list[ValidationSeverityMetric],
    summary="Return failed validations by severity",
)
def get_validation_severity_metrics() -> list[ValidationSeverityMetric]:
    """Return failed validation counts grouped by severity."""
    rows = execute_query(
        """
        SELECT
            COALESCE(severity, 'unknown') AS severity,
            COUNT(*) AS failed_checks
        FROM validation_result
        WHERE is_valid IS FALSE
        GROUP BY COALESCE(severity, 'unknown')
        ORDER BY failed_checks DESC, severity
        """
    )

    return [
        ValidationSeverityMetric(
            severity=row["severity"],
            failed_checks=int(row["failed_checks"]),
        )
        for row in rows
    ]


@router.get(
    "/rejected-records",
    response_model=list[RejectedRecordItem],
    summary="Return detailed rejected records",
)
def get_rejected_records() -> list[RejectedRecordItem]:
    """Return rejected records together with resolution information."""
    rows = execute_query(
        """
        SELECT
            rejected_record_id,
            source_table,
            source_record_id,
            source_file,
            source_row,
            rule_id,
            severity,
            rejection_reason,
            run_id,
            resolution_status,
            corrected_value,
            resolution_note,
            resolved_by,
            resolved_at
        FROM rejected_record
        ORDER BY rejected_at, rejected_record_id
        """
    )

    return [
        RejectedRecordItem(
            rejected_record_id=row["rejected_record_id"],
            source_table=row["source_table"],
            source_record_id=row["source_record_id"],
            source_file=row["source_file"],
            source_row=row["source_row"],
            rule_id=row["rule_id"],
            severity=row["severity"],
            rejection_reason=row["rejection_reason"],
            run_id=row["run_id"],
            resolution_status=row["resolution_status"],
            corrected_value=row["corrected_value"],
            resolution_note=row["resolution_note"],
            resolved_by=row["resolved_by"],
            resolved_at=row["resolved_at"],
        )
        for row in rows
    ]


@router.get(
    "/resolution-status",
    response_model=list[ResolutionStatusMetric],
    summary="Return rejected issues by resolution status",
)
def get_resolution_status_metrics() -> list[ResolutionStatusMetric]:
    """Return issue counts grouped by resolution status."""
    rows = execute_query(
        """
        SELECT
            resolution_status,
            COUNT(*) AS issue_count
        FROM rejected_record
        GROUP BY resolution_status
        ORDER BY resolution_status
        """
    )

    return [
        ResolutionStatusMetric(
            resolution_status=row["resolution_status"],
            issue_count=int(row["issue_count"]),
        )
        for row in rows
    ]


@router.patch(
    "/rejected-records/{rejected_record_id}/resolution",
    response_model=RejectedRecordResolutionResponse,
    summary="Update one rejected-record issue",
)
def patch_rejected_record_resolution(
    rejected_record_id: str,
    update: RejectedRecordResolutionUpdate,
) -> RejectedRecordResolutionResponse:
    """Update the resolution status and notes for one rejected record."""
    updated_row = update_rejected_record_resolution(
        rejected_record_id=rejected_record_id,
        update=update,
    )

    return RejectedRecordResolutionResponse(**updated_row)


@router.get(
    "/lineage",
    response_model=list[LineageStageMetric],
    summary="Return data-lineage stage metrics",
)
def get_lineage_metrics() -> list[LineageStageMetric]:
    """Return counts representing data movement through the pipeline."""
    rows = execute_query(
        """
        SELECT
            (
                SELECT COUNT(DISTINCT source_row)
                FROM validation_result
                WHERE source_table = 'sample'
            ) AS input_sample_records,

            (
                SELECT COUNT(DISTINCT source_row)
                FROM validation_result
                WHERE source_table = 'assay_result'
            ) AS input_assay_records,

            (SELECT COUNT(*) FROM sample) AS accepted_samples,

            (SELECT COUNT(*) FROM assay_result) AS accepted_assay_results,

            (SELECT COUNT(*) FROM shipment) AS accepted_shipments,

            (SELECT COUNT(*) FROM workflow_event)
                AS accepted_workflow_events,

            (SELECT COUNT(*) FROM validation_result)
                AS validation_checks,

            (
                SELECT COUNT(*)
                FROM validation_result
                WHERE is_valid IS FALSE
            ) AS failed_checks,

            (SELECT COUNT(*) FROM rejected_record) AS rejected_records,

            (
                SELECT COUNT(*)
                FROM rejected_record
                WHERE resolution_status = 'open'
            ) AS open_issues,

            (
                SELECT COUNT(*)
                FROM rejected_record
                WHERE resolution_status IN (
                    'corrected',
                    'resolved',
                    'dismissed'
                )
            ) AS handled_issues
        """
    )

    if not rows:
        raise HTTPException(
            status_code=500,
            detail="Lineage query returned no result.",
        )

    row = rows[0]

    return [
        LineageStageMetric(
            stage="Input sample records",
            record_count=int(row["input_sample_records"]),
            explanation=(
                "Distinct sample source rows evaluated by validation."
            ),
        ),
        LineageStageMetric(
            stage="Input assay-result records",
            record_count=int(row["input_assay_records"]),
            explanation=(
                "Distinct assay-result source rows evaluated by validation."
            ),
        ),
        LineageStageMetric(
            stage="Accepted samples",
            record_count=int(row["accepted_samples"]),
            explanation="Valid sample records stored in PostgreSQL.",
        ),
        LineageStageMetric(
            stage="Accepted assay results",
            record_count=int(row["accepted_assay_results"]),
            explanation="Valid assay results stored in PostgreSQL.",
        ),
        LineageStageMetric(
            stage="Accepted shipments",
            record_count=int(row["accepted_shipments"]),
            explanation="Valid shipment records stored in PostgreSQL.",
        ),
        LineageStageMetric(
            stage="Accepted workflow events",
            record_count=int(row["accepted_workflow_events"]),
            explanation="Valid workflow events stored in PostgreSQL.",
        ),
        LineageStageMetric(
            stage="Validation checks",
            record_count=int(row["validation_checks"]),
            explanation=(
                "Total field and record validation checks stored for audit."
            ),
        ),
        LineageStageMetric(
            stage="Failed checks",
            record_count=int(row["failed_checks"]),
            explanation="Validation checks that did not pass.",
        ),
        LineageStageMetric(
            stage="Rejected records",
            record_count=int(row["rejected_records"]),
            explanation=(
                "Audit entries explaining what was rejected and why."
            ),
        ),
        LineageStageMetric(
            stage="Open issues",
            record_count=int(row["open_issues"]),
            explanation=(
                "Rejected-record issues that still require handling."
            ),
        ),
        LineageStageMetric(
            stage="Handled issues",
            record_count=int(row["handled_issues"]),
            explanation=(
                "Issues marked as corrected, resolved, or dismissed."
            ),
        ),
    ]


@router.get(
    "/documentation",
    response_model=DashboardDocumentationResponse,
    summary="Return dashboard documentation",
)
def get_dashboard_documentation() -> DashboardDocumentationResponse:
    """Return documentation content for the Streamlit page."""
    return DashboardDocumentationResponse(
        title="Synthetic Lab Pipeline Governance Dashboard",
        purpose=(
            "Visualize accepted laboratory data and monitor validation, "
            "rejection, lineage, and issue-resolution information."
        ),
        data_area=[
            "Accepted sample, result, shipment, and workflow-event counts",
            "Assay-result metrics grouped by analyte",
            "Sample-level result, shipment, and workflow-event summaries",
        ],
        governance_area=[
            "Passed and failed validation counts",
            "Failures grouped by validation rule",
            "Failures grouped by severity",
            "Detailed rejected-record information",
            "Pipeline-stage lineage counts",
            "Open, corrected, resolved, and dismissed issue tracking",
        ],
        lineage_definition=(
            "Data lineage describes what entered the pipeline, which checks "
            "were performed, which records were accepted, and which records "
            "were rejected with their reasons."
        ),
        resolution_definition=(
            "Issue-resolution tracking records whether a rejected data issue "
            "is still open or has been corrected, resolved, or dismissed. "
            "It can also store a corrected value, a note, the responsible "
            "person or process, and the resolution time."
        ),
        data_source=(
            "Local PostgreSQL database populated by the one-time M9 loader."
        ),
    )