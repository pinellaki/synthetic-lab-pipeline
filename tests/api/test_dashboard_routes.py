from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from src.main import app
from src.api import dashboard_routes


client = TestClient(app)


def test_dashboard_overview_endpoint(monkeypatch):
    def fake_execute_query(query, params=None):
        return [
            {
                "samples": 2,
                "assay_results": 2,
                "shipments": 2,
                "workflow_events": 4,
                "validation_results": 46,
                "passed_validations": 39,
                "failed_validations": 7,
                "rejected_records": 7,
                "open_issues": 6,
                "resolved_issues": 1,
            }
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/overview")

    assert response.status_code == 200
    assert response.json() == {
        "samples": 2,
        "assay_results": 2,
        "shipments": 2,
        "workflow_events": 4,
        "validation_results": 46,
        "passed_validations": 39,
        "failed_validations": 7,
        "rejected_records": 7,
        "open_issues": 6,
        "resolved_issues": 1,
        "validation_pass_rate": 84.78,
    }


def test_dashboard_lab_results_endpoint(monkeypatch):
    def fake_execute_query(query, params=None):
        return [
            {
                "analyte_code": "CREA",
                "analyte_name": "Creatinine",
                "canonical_unit": "mg/dL",
                "result_count": 1,
                "average_value": Decimal("1.1"),
                "minimum_value": Decimal("1.1"),
                "maximum_value": Decimal("1.1"),
            },
            {
                "analyte_code": "GLU",
                "analyte_name": "Glucose",
                "canonical_unit": "mg/dL",
                "result_count": 1,
                "average_value": Decimal("95.0"),
                "minimum_value": Decimal("95.0"),
                "maximum_value": Decimal("95.0"),
            },
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/lab-results")

    assert response.status_code == 200
    assert response.json() == [
        {
            "analyte_code": "CREA",
            "analyte_name": "Creatinine",
            "canonical_unit": "mg/dL",
            "result_count": 1,
            "average_value": 1.1,
            "minimum_value": 1.1,
            "maximum_value": 1.1,
        },
        {
            "analyte_code": "GLU",
            "analyte_name": "Glucose",
            "canonical_unit": "mg/dL",
            "result_count": 1,
            "average_value": 95.0,
            "minimum_value": 95.0,
            "maximum_value": 95.0,
        },
    ]


def test_dashboard_resolution_status_endpoint(monkeypatch):
    def fake_execute_query(query, params=None):
        return [
            {
                "resolution_status": "corrected",
                "issue_count": 1,
            },
            {
                "resolution_status": "open",
                "issue_count": 6,
            },
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/resolution-status")

    assert response.status_code == 200
    assert response.json() == [
        {
            "resolution_status": "corrected",
            "issue_count": 1,
        },
        {
            "resolution_status": "open",
            "issue_count": 6,
        },
    ]


def test_dashboard_source_document_summary_endpoint(monkeypatch):
    def fake_execute_query(query, params=None):
        return [
            {
                "source_type": "API_JSON",
                "ingestion_status": "processed",
                "file_count": 3,
                "total_records_detected": 121,
            },
            {
                "source_type": "PDF_REPORT",
                "ingestion_status": "detected_only",
                "file_count": 6,
                "total_records_detected": 6,
            },
            {
                "source_type": "TEXT_REPORT",
                "ingestion_status": "detected_only",
                "file_count": 12,
                "total_records_detected": 120,
            },
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/source-document-summary")

    assert response.status_code == 200
    assert response.json() == [
        {
            "source_type": "API_JSON",
            "ingestion_status": "processed",
            "file_count": 3,
            "total_records_detected": 121,
        },
        {
            "source_type": "PDF_REPORT",
            "ingestion_status": "detected_only",
            "file_count": 6,
            "total_records_detected": 6,
        },
        {
            "source_type": "TEXT_REPORT",
            "ingestion_status": "detected_only",
            "file_count": 12,
            "total_records_detected": 120,
        },
    ]


def test_dashboard_source_documents_endpoint(monkeypatch):
    source_timestamp = datetime(2026, 6, 22, 13, 40, 37, 914348)

    def fake_execute_query(query, params=None):
        return [
            {
                "source_document_id": 1,
                "source_path": "data/raw/api_pages/shipments_page_1.json",
                "file_name": "shipments_page_1.json",
                "source_type": "API_JSON",
                "file_extension": ".json",
                "file_size_bytes": 13509,
                "records_detected": 45,
                "records_loaded": None,
                "records_rejected": None,
                "ingestion_status": "processed",
                "notes": (
                    "Structured source detected. This source type can be used "
                    "by the pipeline for loading trusted PostgreSQL tables."
                ),
                "ingested_at": source_timestamp,
                "updated_at": source_timestamp,
            }
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/source-documents")

    assert response.status_code == 200
    assert response.json() == [
        {
            "source_document_id": 1,
            "source_path": "data/raw/api_pages/shipments_page_1.json",
            "file_name": "shipments_page_1.json",
            "source_type": "API_JSON",
            "file_extension": ".json",
            "file_size_bytes": 13509,
            "records_detected": 45,
            "records_loaded": None,
            "records_rejected": None,
            "ingestion_status": "processed",
            "notes": (
                "Structured source detected. This source type can be used "
                "by the pipeline for loading trusted PostgreSQL tables."
            ),
            "ingested_at": "2026-06-22T13:40:37.914348",
            "updated_at": "2026-06-22T13:40:37.914348",
        }
    ]


def test_dashboard_lineage_endpoint(monkeypatch):
    def fake_execute_query(query, params=None):
        return [
            {
                "source_documents": 30,
                "pdf_reports": 6,
                "text_reports": 12,
                "input_sample_records": 4,
                "input_assay_records": 5,
                "accepted_samples": 2,
                "accepted_assay_results": 2,
                "accepted_shipments": 2,
                "accepted_workflow_events": 4,
                "validation_checks": 46,
                "failed_checks": 7,
                "rejected_records": 7,
                "open_issues": 6,
                "handled_issues": 1,
            }
        ]

    monkeypatch.setattr(dashboard_routes, "execute_query", fake_execute_query)

    response = client.get("/dashboard/lineage")

    assert response.status_code == 200
    assert response.json() == [
        {
            "stage": "Raw source files detected",
            "record_count": 30,
            "explanation": (
                "CSV, Excel, API JSON, PDF, and text files detected in data/raw."
            ),
        },
        {
            "stage": "PDF reports detected",
            "record_count": 6,
            "explanation": "PDF reports tracked as raw source metadata.",
        },
        {
            "stage": "Text reports detected",
            "record_count": 12,
            "explanation": "Text reports tracked as raw source metadata.",
        },
        {
            "stage": "Input sample records",
            "record_count": 4,
            "explanation": "Distinct sample source rows evaluated by validation.",
        },
        {
            "stage": "Input assay-result records",
            "record_count": 5,
            "explanation": (
                "Distinct assay-result source rows evaluated by validation."
            ),
        },
        {
            "stage": "Accepted samples",
            "record_count": 2,
            "explanation": "Valid sample records stored in PostgreSQL.",
        },
        {
            "stage": "Accepted assay results",
            "record_count": 2,
            "explanation": "Valid assay results stored in PostgreSQL.",
        },
        {
            "stage": "Accepted shipments",
            "record_count": 2,
            "explanation": "Valid shipment records stored in PostgreSQL.",
        },
        {
            "stage": "Accepted workflow events",
            "record_count": 4,
            "explanation": "Valid workflow events stored in PostgreSQL.",
        },
        {
            "stage": "Validation checks",
            "record_count": 46,
            "explanation": "Total field and record validation checks stored for audit.",
        },
        {
            "stage": "Failed checks",
            "record_count": 7,
            "explanation": "Validation checks that did not pass.",
        },
        {
            "stage": "Rejected records",
            "record_count": 7,
            "explanation": "Audit entries explaining what was rejected and why.",
        },
        {
            "stage": "Open issues",
            "record_count": 6,
            "explanation": "Rejected-record issues that still require handling.",
        },
        {
            "stage": "Handled issues",
            "record_count": 1,
            "explanation": "Issues marked as corrected, resolved, or dismissed.",
        },
    ]


def test_update_rejected_record_resolution_endpoint(monkeypatch):
    def fake_update_rejected_record_resolution(rejected_record_id, update):
        return {
            "rejected_record_id": rejected_record_id,
            "resolution_status": update.resolution_status,
            "corrected_value": update.corrected_value,
            "resolution_note": update.resolution_note,
            "resolved_by": update.resolved_by,
            "resolved_at": "2026-06-17T12:03:27.311681",
        }

    monkeypatch.setattr(
        dashboard_routes,
        "update_rejected_record_resolution",
        fake_update_rejected_record_resolution,
    )

    response = client.patch(
        "/dashboard/rejected-records/1/resolution",
        json={
            "resolution_status": "corrected",
            "corrected_value": "SMP-003",
            "resolution_note": "Missing sample ID was reviewed and assigned",
            "resolved_by": "Elina",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "rejected_record_id": "1",
        "resolution_status": "corrected",
        "corrected_value": "SMP-003",
        "resolution_note": "Missing sample ID was reviewed and assigned",
        "resolved_by": "Elina",
        "resolved_at": "2026-06-17T12:03:27.311681",
    }