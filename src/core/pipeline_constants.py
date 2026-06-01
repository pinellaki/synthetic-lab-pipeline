"""Project-wide constants for the Synthetic Lab Pipeline.

This module defines constant values reused across the pipeline.

Constants are centralized here so the same values are not repeated in multiple
files. This makes the project easier to maintain and reduces the risk of using
different values in different parts of the code.
"""


class PipelineConstants:
    """Store shared constant values used by the pipeline.

    Constants:
        SAMPLE_ID_PREFIX: Expected prefix for standardized sample identifiers.
        SUBJECT_ID_PREFIX: Expected prefix for standardized subject identifiers.

        RAW_LAYER: Name of the raw data layer.
        STAGING_LAYER: Name of the staging data layer.
        TRUSTED_LAYER: Name of the trusted data layer.
        REJECTED_LAYER: Name of the rejected data layer.

        CSV_EXTENSION: File extension for CSV files.
        JSON_EXTENSION: File extension for JSON files.
        EXCEL_EXTENSION: File extension for Excel files.
        TEXT_EXTENSION: File extension for text files.
        PDF_EXTENSION: File extension for PDF files.

        ACCEPTED_QC_STATUSES: Allowed quality control status values.

        BOOLEAN_TRUE_VALUES: Raw values that should be interpreted as True.
        BOOLEAN_FALSE_VALUES: Raw values that should be interpreted as False.
    """

    SAMPLE_ID_PREFIX = "SMP"
    SUBJECT_ID_PREFIX = "SUBJ"

    RAW_LAYER = "raw"
    STAGING_LAYER = "staging"
    TRUSTED_LAYER = "trusted"
    REJECTED_LAYER = "rejected"

    CSV_EXTENSION = ".csv"
    JSON_EXTENSION = ".json"
    EXCEL_EXTENSION = ".xlsx"
    TEXT_EXTENSION = ".txt"
    PDF_EXTENSION = ".pdf"

    ACCEPTED_QC_STATUSES = {
        "OK",
        "PASS",
        "REVIEW",
        "FAIL",
    }

    BOOLEAN_TRUE_VALUES = {
        "true",
        "yes",
        "y",
        "1",
    }

    BOOLEAN_FALSE_VALUES = {
        "false",
        "no",
        "n",
        "0",
    }