"""Reference data used by the one-time PostgreSQL load.

This module contains the small controlled datasets that must be inserted before
samples, assay results, validation results, and rejected records.

The values are based on the fake M8 example data and the existing Python
validation rules.
"""


SITE_ROWS = [
    {
        "site_code": "MILAN",
        "site_name": "Milan Laboratory Site",
        "country": "Italy",
        "site_type": "laboratory",
        "source_file": "sample_submissions.csv",
        "source_row": None,
    },
    {
        "site_code": "TURIN",
        "site_name": "Turin Laboratory Site",
        "country": "Italy",
        "site_type": "laboratory",
        "source_file": "sample_submissions.csv",
        "source_row": None,
    },
    {
        "site_code": "ROME",
        "site_name": "Rome Laboratory Site",
        "country": "Italy",
        "site_type": "laboratory",
        "source_file": "sample_submissions.csv",
        "source_row": None,
    },
]


ANALYTE_ROWS = [
    {
        "analyte_code": "GLU",
        "analyte_name": "Glucose",
        "canonical_unit": "mg/dL",
        "reference_low": None,
        "reference_high": None,
        "source_file": "assay_results.csv",
        "source_row": None,
    },
    {
        "analyte_code": "CREA",
        "analyte_name": "Creatinine",
        "canonical_unit": "mg/dL",
        "reference_low": None,
        "reference_high": None,
        "source_file": "assay_results.csv",
        "source_row": None,
    },
    {
        "analyte_code": "ALT",
        "analyte_name": "Alanine aminotransferase",
        "canonical_unit": "U/L",
        "reference_low": None,
        "reference_high": None,
        "source_file": "assay_results.csv",
        "source_row": None,
    },
]


VALIDATION_RULE_ROWS = [
    {
        "rule_id": "S1",
        "target_table": "sample",
        "target_field": "sample_id",
        "severity": "critical",
        "action": "reject",
        "description": "sample_id is required.",
    },
    {
        "rule_id": "S4",
        "target_table": "sample",
        "target_field": "subject_id",
        "severity": "high",
        "action": "review",
        "description": "subject_id is required.",
    },
    {
        "rule_id": "S8",
        "target_table": "sample",
        "target_field": "collection_datetime",
        "severity": "high",
        "action": "review",
        "description": (
            "collection_datetime and received_datetime must be parseable, "
            "and collection_datetime cannot be after received_datetime."
        ),
    },
    {
        "rule_id": "S10",
        "target_table": "sample",
        "target_field": "intake_temperature_c",
        "severity": "high",
        "action": "review",
        "description": "intake_temperature_c must be numeric.",
    },
    {
        "rule_id": "R1",
        "target_table": "assay_result",
        "target_field": "result_id",
        "severity": "critical",
        "action": "reject",
        "description": "result_id is required.",
    },
    {
        "rule_id": "R2",
        "target_table": "assay_result",
        "target_field": "sample_id",
        "severity": "critical",
        "action": "reject",
        "description": "sample_id is required.",
    },
    {
        "rule_id": "R4",
        "target_table": "assay_result",
        "target_field": "analyte_code",
        "severity": "critical",
        "action": "reject",
        "description": "analyte_code is required.",
    },
    {
        "rule_id": "R6",
        "target_table": "assay_result",
        "target_field": "result_value",
        "severity": "critical",
        "action": "reject",
        "description": "result_value is required and must be numeric.",
    },
    {
        "rule_id": "R7",
        "target_table": "assay_result",
        "target_field": "result_value",
        "severity": "critical",
        "action": "reject",
        "description": "result_value must be non-negative.",
    },
    {
        "rule_id": "R9",
        "target_table": "assay_result",
        "target_field": "unit",
        "severity": "high",
        "action": "review",
        "description": "unit is required.",
    },
]