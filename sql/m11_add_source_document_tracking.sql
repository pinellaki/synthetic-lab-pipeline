-- Add source-document tracking for raw files entering the pipeline.
--
-- This table tracks source files such as CSV files, Excel workbooks,
-- API JSON pages, PDF reports, and text reports.
--
-- It is intentionally metadata-focused: it records which files entered
-- the pipeline and basic counts such as rows, pages, or detected records.

CREATE TABLE IF NOT EXISTS source_document (
    source_document_id BIGSERIAL PRIMARY KEY,
    source_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    file_extension TEXT,
    file_size_bytes BIGINT,
    records_detected INTEGER,
    records_loaded INTEGER,
    records_rejected INTEGER,
    ingestion_status TEXT NOT NULL DEFAULT 'detected_only',
    notes TEXT,
    ingested_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT source_document_source_type_check CHECK (
        source_type IN (
            'CSV',
            'EXCEL',
            'API_JSON',
            'PDF_REPORT',
            'TEXT_REPORT',
            'OTHER'
        )
    ),
    CONSTRAINT source_document_ingestion_status_check CHECK (
        ingestion_status IN (
            'processed',
            'detected_only',
            'skipped',
            'error'
        )
    )
);

COMMENT ON TABLE source_document IS
    'Tracks raw source files and reports detected by the pipeline.';

COMMENT ON COLUMN source_document.source_path IS
    'Relative path of the source file inside the project.';

COMMENT ON COLUMN source_document.source_type IS
    'Source category such as CSV, EXCEL, API_JSON, PDF_REPORT, or TEXT_REPORT.';

COMMENT ON COLUMN source_document.records_detected IS
    'Detected rows, records, pages, or lines depending on the source type.';

COMMENT ON COLUMN source_document.records_loaded IS
    'Optional count of records loaded from this source into trusted tables.';

COMMENT ON COLUMN source_document.records_rejected IS
    'Optional count of records rejected from this source.';

COMMENT ON COLUMN source_document.ingestion_status IS
    'Whether the source was processed, detected only, skipped, or had an error.';