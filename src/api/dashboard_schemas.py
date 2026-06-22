"""Pydantic models for the governance dashboard API.

These models describe the data returned by the dashboard endpoints and the
data accepted when a rejected-record issue is corrected or resolved.

The dashboard covers:

1. laboratory and accepted business data
2. validation and rejection governance
3. pipeline lineage
4. rejected-record issue resolution
5. raw source-document tracking
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ResolutionStatus = Literal[
    "open",
    "corrected",
    "resolved",
    "dismissed",
]


class DashboardOverviewResponse(BaseModel):
    """High-level PostgreSQL dashboard counters."""

    samples: int = Field(
        description="Number of accepted samples stored in PostgreSQL."
    )
    assay_results: int = Field(
        description="Number of accepted assay results."
    )
    shipments: int = Field(
        description="Number of accepted shipment records."
    )
    workflow_events: int = Field(
        description="Number of accepted workflow events."
    )
    validation_results: int = Field(
        description="Total number of validation checks performed."
    )
    passed_validations: int = Field(
        description="Number of validation checks that passed."
    )
    failed_validations: int = Field(
        description="Number of validation checks that failed."
    )
    rejected_records: int = Field(
        description="Number of rejected-record audit entries."
    )
    open_issues: int = Field(
        description="Number of rejected-record issues still marked as open."
    )
    resolved_issues: int = Field(
        description=(
            "Number of rejected-record issues marked as corrected, resolved, "
            "or dismissed."
        )
    )
    validation_pass_rate: float = Field(
        description="Percentage of validation checks that passed."
    )


class LabResultMetric(BaseModel):
    """Aggregated assay-result information for one analyte."""

    analyte_code: str = Field(
        description="Controlled analyte identifier."
    )
    analyte_name: str = Field(
        description="Human-readable analyte name."
    )
    canonical_unit: str = Field(
        description="Canonical measurement unit."
    )
    result_count: int = Field(
        description="Number of stored results for the analyte."
    )
    average_value: float | None = Field(
        description="Average result value."
    )
    minimum_value: float | None = Field(
        description="Minimum result value."
    )
    maximum_value: float | None = Field(
        description="Maximum result value."
    )


class SampleSummaryItem(BaseModel):
    """Detailed sample summary for the dashboard."""

    sample_id: str = Field(
        description="Unique sample identifier."
    )
    subject_id: str = Field(
        description="Subject identifier associated with the sample."
    )
    collection_site_code: str | None = Field(
        description="Collection-site code."
    )
    site_name: str | None = Field(
        description="Human-readable collection-site name."
    )
    sample_type: str | None = Field(
        description="Type of biological sample."
    )
    priority: str | None = Field(
        description="Sample processing priority."
    )
    assay_result_count: int = Field(
        description="Number of assay results for the sample."
    )
    shipment_count: int = Field(
        description="Number of shipments for the sample."
    )
    workflow_event_count: int = Field(
        description="Number of workflow events for the sample."
    )
    has_retry_or_repeat_message: bool = Field(
        description=(
            "Whether workflow history contains a retry or repeat message."
        )
    )


class ValidationRuleMetric(BaseModel):
    """Aggregated validation results for one rule."""

    rule_id: str = Field(
        description="Validation-rule identifier."
    )
    description: str = Field(
        description="Validation-rule description."
    )
    severity: str = Field(
        description="Configured rule severity."
    )
    action: str = Field(
        description="Configured action when the rule fails."
    )
    total_checks: int = Field(
        description="Number of times the rule was evaluated."
    )
    passed_checks: int = Field(
        description="Number of successful validations."
    )
    failed_checks: int = Field(
        description="Number of failed validations."
    )


class ValidationSeverityMetric(BaseModel):
    """Aggregated validation failures by severity."""

    severity: str = Field(
        description="Validation severity."
    )
    failed_checks: int = Field(
        description="Number of failed checks with this severity."
    )


class RejectedRecordItem(BaseModel):
    """Detailed rejected-record and resolution information."""

    rejected_record_id: str = Field(
        description="Unique rejected-record identifier."
    )
    source_table: str | None = Field(
        description="Business table associated with the source record."
    )
    source_record_id: str | None = Field(
        description="Identifier of the rejected source record."
    )
    source_file: str | None = Field(
        description="Source file containing the rejected record."
    )
    source_row: int | None = Field(
        description="Row number in the source file."
    )
    rule_id: str | None = Field(
        description="Validation rule that caused the rejection."
    )
    severity: str | None = Field(
        description="Severity of the rejection."
    )
    rejection_reason: str = Field(
        description="Explanation of why the record was rejected."
    )
    run_id: str | None = Field(
        description="Pipeline run that produced the rejection."
    )
    resolution_status: ResolutionStatus = Field(
        description="Current issue-resolution status."
    )
    corrected_value: str | None = Field(
        description="Corrected value, when a correction was supplied."
    )
    resolution_note: str | None = Field(
        description="Explanation of how the issue was handled."
    )
    resolved_by: str | None = Field(
        description="Person or process that handled the issue."
    )
    resolved_at: datetime | None = Field(
        description="Date and time when the issue was handled."
    )


class ResolutionStatusMetric(BaseModel):
    """Aggregated rejected-record issues by resolution status."""

    resolution_status: ResolutionStatus = Field(
        description="Issue-resolution status."
    )
    issue_count: int = Field(
        description="Number of rejected records with this status."
    )


class RejectedRecordResolutionUpdate(BaseModel):
    """Request body for changing one rejected-record resolution status."""

    resolution_status: ResolutionStatus = Field(
        description="New issue-resolution status."
    )
    corrected_value: str | None = Field(
        default=None,
        description="Corrected value, when applicable."
    )
    resolution_note: str | None = Field(
        default=None,
        description="Explanation of how the issue was handled."
    )
    resolved_by: str | None = Field(
        default=None,
        description="Person or process handling the issue."
    )


class RejectedRecordResolutionResponse(BaseModel):
    """Response returned after updating one rejected-record issue."""

    rejected_record_id: str = Field(
        description="Rejected record that was updated."
    )
    resolution_status: ResolutionStatus = Field(
        description="Current issue-resolution status."
    )
    corrected_value: str | None = Field(
        description="Stored corrected value."
    )
    resolution_note: str | None = Field(
        description="Stored resolution explanation."
    )
    resolved_by: str | None = Field(
        description="Person or process that handled the issue."
    )
    resolved_at: datetime | None = Field(
        description="Date and time when the issue was handled."
    )


class LineageStageMetric(BaseModel):
    """Count of records at one logical pipeline stage."""

    stage: str = Field(
        description="Pipeline or governance stage."
    )
    record_count: int = Field(
        description="Number of records represented at the stage."
    )
    explanation: str = Field(
        description="Meaning of the stage and its count."
    )


class SourceDocumentSummaryMetric(BaseModel):
    """Aggregated raw source-document counts."""

    source_type: str = Field(
        description="Source type such as CSV, API_JSON, PDF_REPORT, or TEXT_REPORT."
    )
    ingestion_status: str = Field(
        description="Processing status such as processed or detected_only."
    )
    file_count: int = Field(
        description="Number of files in this source/status group."
    )
    total_records_detected: int = Field(
        description="Total rows, records, pages, or lines detected."
    )


class SourceDocumentItem(BaseModel):
    """Detailed metadata for one raw source document."""

    source_document_id: int = Field(
        description="Unique source-document metadata identifier."
    )
    source_path: str = Field(
        description="Relative path of the source file inside the project."
    )
    file_name: str = Field(
        description="Source file name."
    )
    source_type: str = Field(
        description="Source type such as CSV, API_JSON, PDF_REPORT, or TEXT_REPORT."
    )
    file_extension: str | None = Field(
        description="File extension."
    )
    file_size_bytes: int | None = Field(
        description="File size in bytes."
    )
    records_detected: int | None = Field(
        description="Detected rows, records, pages, or lines."
    )
    records_loaded: int | None = Field(
        description="Optional count of loaded records from this source."
    )
    records_rejected: int | None = Field(
        description="Optional count of rejected records from this source."
    )
    ingestion_status: str = Field(
        description="Whether the source was processed, detected only, skipped, or errored."
    )
    notes: str | None = Field(
        description="Governance note about how the source was handled."
    )
    ingested_at: datetime = Field(
        description="Date and time when the source metadata was first loaded."
    )
    updated_at: datetime = Field(
        description="Date and time when the source metadata was last updated."
    )


class DashboardDocumentationResponse(BaseModel):
    """Documentation information displayed by the dashboard."""

    title: str = Field(
        description="Dashboard documentation title."
    )
    purpose: str = Field(
        description="Purpose of the governance dashboard."
    )
    data_area: list[str] = Field(
        description="Metrics available in the laboratory-data area."
    )
    governance_area: list[str] = Field(
        description="Metrics available in the governance area."
    )
    source_document_area: list[str] = Field(
        description="Metrics available for raw source-document tracking."
    )
    lineage_definition: str = Field(
        description="Explanation of data lineage in this project."
    )
    resolution_definition: str = Field(
        description="Explanation of rejected-record issue tracking."
    )
    source_document_definition: str = Field(
        description="Explanation of raw file and report tracking."
    )
    data_source: str = Field(
        description="Source used by the dashboard."
    )