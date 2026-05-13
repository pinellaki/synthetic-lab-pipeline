class PipelineConstants:
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