"""FastAPI routes for exposing the M8 fake-data pipeline.

This module defines API endpoints that describe and summarize the M8 pipeline.

The goal is to make the pipeline visible through FastAPI automatic
documentation. These endpoints use fake sample data only and do not load
records into PostgreSQL.
"""

from fastapi import APIRouter

from src.api.m8_schemas import (
    EndpointInfo,
    M8PipelineSummaryResponse,
    M8SampleDataSummaryResponse,
    RejectedRecordsSummaryResponse,
    SchemaInfo,
)
from src.pipeline.sample_data_rejection_test import build_rejected_records
from src.pipeline.sample_data_schema_test import (
    build_assay_results,
    build_sample_submissions,
    build_shipments,
    build_workflow_events,
)


router = APIRouter(
    prefix="/m8",
    tags=["M8 fake-data pipeline"],
)


@router.get(
    "/endpoints",
    response_model=list[EndpointInfo],
    summary="List M8 API endpoints",
)
def list_m8_endpoints() -> list[EndpointInfo]:
    """Return the list of M8 documentation endpoints.

    Returns:
        List of endpoint descriptions exposed for the M8 fake-data pipeline.
    """
    return [
        EndpointInfo(
            path="/m8/endpoints",
            method="GET",
            summary="List M8 API endpoints",
            purpose="Shows the available M8 documentation endpoints.",
        ),
        EndpointInfo(
            path="/m8/schemas",
            method="GET",
            summary="List M8 schemas",
            purpose="Shows the main Pydantic schemas used by the M8 pipeline.",
        ),
        EndpointInfo(
            path="/m8/sample-data/summary",
            method="GET",
            summary="Summarize fake input data",
            purpose="Shows how many fake records are read from each input file.",
        ),
        EndpointInfo(
            path="/m8/pipeline/summary",
            method="GET",
            summary="Summarize M8 pipeline flow",
            purpose="Shows the end-to-end M8 fake-data pipeline summary.",
        ),
        EndpointInfo(
            path="/m8/rejected-records/summary",
            method="GET",
            summary="Summarize rejected records",
            purpose="Shows how many rejected records are created by validation.",
        ),
    ]


@router.get(
    "/schemas",
    response_model=list[SchemaInfo],
    summary="List M8 Pydantic schemas",
)
def list_m8_schemas() -> list[SchemaInfo]:
    """Return the main Pydantic schemas used by the M8 pipeline.

    Returns:
        List of schema descriptions.
    """
    return [
        SchemaInfo(
            name="IngestionMetadata",
            layer="schemas",
            purpose="Stores source traceability for each ingested record.",
            important_fields=[
                "source_file",
                "source_row",
                "run_id",
                "ingested_at",
            ],
        ),
        SchemaInfo(
            name="SampleSubmissionRaw",
            layer="schemas",
            purpose="Represents one raw sample submission record.",
            important_fields=[
                "sample_id",
                "subject_id",
                "collection_site",
                "collection_datetime",
                "received_datetime",
                "metadata",
            ],
        ),
        SchemaInfo(
            name="AssayResultRaw",
            layer="schemas",
            purpose="Represents one raw assay result record.",
            important_fields=[
                "result_id",
                "sample_id",
                "analyte_code",
                "result_value_raw",
                "unit_raw",
                "metadata",
            ],
        ),
        SchemaInfo(
            name="ShipmentRaw",
            layer="schemas",
            purpose="Represents one raw shipment record.",
            important_fields=[
                "shipment_id",
                "sample_id",
                "courier",
                "shipped_at_raw",
                "received_at_raw",
                "metadata",
            ],
        ),
        SchemaInfo(
            name="WorkflowEventRaw",
            layer="schemas",
            purpose="Represents one raw workflow status event.",
            important_fields=[
                "event_id",
                "sample_id",
                "event_status",
                "event_timestamp_raw",
                "actor",
                "metadata",
            ],
        ),
        SchemaInfo(
            name="ValidationResult",
            layer="schemas",
            purpose="Represents the result of one validation rule.",
            important_fields=[
                "is_valid",
                "rule_id",
                "severity",
                "message",
                "action",
            ],
        ),
        SchemaInfo(
            name="RejectedRecord",
            layer="rejection",
            purpose="Represents one record rejected by validation.",
            important_fields=[
                "source_file",
                "source_record_id",
                "rule_id",
                "severity",
                "rejection_reason",
                "run_id",
            ],
        ),
    ]


@router.get(
    "/sample-data/summary",
    response_model=M8SampleDataSummaryResponse,
    summary="Summarize M8 fake sample data",
)
def get_m8_sample_data_summary() -> M8SampleDataSummaryResponse:
    """Return record counts for the M8 fake input files.

    Returns:
        Summary of fake input files and record counts.
    """
    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()
    shipments = build_shipments()
    workflow_events = build_workflow_events()

    return M8SampleDataSummaryResponse(
        source_folder="data/raw/examples",
        sample_submissions_count=len(sample_submissions),
        assay_results_count=len(assay_results),
        shipments_count=len(shipments),
        workflow_events_count=len(workflow_events),
        uses_real_data=False,
        loads_postgresql=False,
    )


@router.get(
    "/pipeline/summary",
    response_model=M8PipelineSummaryResponse,
    summary="Summarize the M8 fake-data pipeline",
)
def get_m8_pipeline_summary() -> M8PipelineSummaryResponse:
    """Return an end-to-end summary of the M8 fake-data pipeline.

    Returns:
        Summary of read records and rejected records created by validation.
    """
    sample_submissions = build_sample_submissions()
    assay_results = build_assay_results()
    shipments = build_shipments()
    workflow_events = build_workflow_events()
    rejected_records = build_rejected_records()

    return M8PipelineSummaryResponse(
        sample_submissions_read=len(sample_submissions),
        assay_results_read=len(assay_results),
        shipments_read=len(shipments),
        workflow_events_read=len(workflow_events),
        rejected_records_created=len(rejected_records),
        pipeline_stage="fake-data ingestion, schema conversion, validation, rejection",
        uses_real_data=False,
        loads_postgresql=False,
    )


@router.get(
    "/rejected-records/summary",
    response_model=RejectedRecordsSummaryResponse,
    summary="Summarize M8 rejected records",
)
def get_m8_rejected_records_summary() -> RejectedRecordsSummaryResponse:
    """Return summary information about M8 rejected records.

    Returns:
        Summary of rejected records created from fake validation failures.
    """
    rejected_records = build_rejected_records()

    return RejectedRecordsSummaryResponse(
        rejected_records_created=len(rejected_records),
        output_file="data/rejected/m8_rejected_records.csv",
        output_is_generated=True,
        tracked_by_git=False,
    )