-- M5 normalized database schema for Synthetic Lab Pipeline
-- Purpose:
-- Define a normalized database structure with clear keys,
-- relationships, audit fields, and indexes.
--
-- Design notes:
-- 1. Normalized tables are the source of truth.
-- 2. Dimension/reference tables store controlled values.
-- 3. Fact/event tables store business events and measurements.
-- 4. Views can simplify complex joins without duplicating data.
-- 5. Denormalized tables can be added later only when queries become too complex or slow.

-- This script creates the normalized database schema for the lab pipeline.
-- It first removes old views and tables if they already exist.
-- Then it creates reference tables, business tables, audit tables, indexes, and a summary view.
-- The goal is to store clean data with clear relationships and quality checks.

-- ============================================================
-- Drop existing objects
-- ============================================================

-- Delete this view if it already exists.
-- This avoids an error when we run the script again.
-- A view is like a saved query, not a real table with stored data.
--A view is not a physical table. It is like a reusable SELECT query saved with a name.
--If the view sample_quality_summary_view already exists, remove it before creating it again.
DROP VIEW IF EXISTS sample_quality_summary_view;

-- Delete this table if it already exists.
-- This lets us recreate the table from zero.
-- IF EXISTS prevents an error if the table does not exist yet.
--DROP TABLE means the table structure is deleted
--That means:
--table removed
--columns removed
--data removed

--Why are there many DROP TABLE lines?
-- Remove old tables before creating the new version.
-- The order matters because some tables depend on other tables.
-- Child tables are dropped before parent tables to avoid foreign key problems.
--Example: assay_result depends on sample. So you drop assay_result before sample. Because if a table is using another table, the database may not let you delete the parent first.
DROP TABLE IF EXISTS rejected_record;
DROP TABLE IF EXISTS validation_result;
DROP TABLE IF EXISTS workflow_event;
DROP TABLE IF EXISTS shipment;
DROP TABLE IF EXISTS assay_result;
DROP TABLE IF EXISTS sample;
DROP TABLE IF EXISTS dim_analyte;
DROP TABLE IF EXISTS dim_site;
DROP TABLE IF EXISTS validation_rule;


-- ============================================================
-- Dimension table: dim_site
-- Dimension tables store reference data. This avoids repeating the same information many times.
-- Example: Instead of writing the full site name in every sample row, you store it once in dim_site. Then the sample table only keeps the site_code.
-- Purpose: Store controlled collection/processing site values.
-- Normalization reason: Site details should not be repeated in every sample row.
-- ============================================================
-- This table stores the list of valid sites.
-- Each site has one unique site_code.
-- We store site information here so we do not repeat it in every sample.
-- source_file and source_row help us know where the data came from.
-- created_at saves when the row was created.

CREATE TABLE dim_site (
-- PRIMARY KEY means this column uniquely identifies each row.
-- No two rows can have the same value here.
-- It also cannot be empty.
    site_code TEXT PRIMARY KEY,
    site_name TEXT NOT NULL,
    country TEXT,
    site_type TEXT,

    source_file TEXT,
    source_row INTEGER,
-- TIMESTAMP means this column stores date and time
--DEFAULT CURRENT_TIMESTAMP If no value is provided, the database automatically saves the current date and time.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Dimension table: dim_analyte.
-- Purpose: Store controlled analyte reference information.
-- Normalization reason: Analyte names, canonical units, and reference ranges should be stored once.
-- ============================================================
-- This table stores the list of valid analytes/tests.
-- Each analyte has one unique analyte_code.
-- It stores the official unit and the normal reference range.
-- This avoids repeating analyte details in every result row.

CREATE TABLE dim_analyte (
    analyte_code TEXT PRIMARY KEY,
    analyte_name TEXT NOT NULL,
    canonical_unit TEXT NOT NULL,
-- NUMERIC means this column stores numbers, including decimals.
    reference_low NUMERIC,
    reference_high NUMERIC,

    source_file TEXT,
    source_row INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Dimension table: validation_rule
-- Purpose: Store validation rule definitions.
-- Normalization reason: Rule metadata should be stored once and referenced by validation results.
-- ============================================================
-- A validation rule says what must be checked in the data.
-- Example: result_value cannot be negative.
-- We store rules once and then reuse them in validation results.

CREATE TABLE validation_rule (
    rule_id TEXT PRIMARY KEY,
    target_table TEXT NOT NULL,
    target_field TEXT,
    severity TEXT NOT NULL,
    action TEXT NOT NULL,
    description TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- Core table: sample
-- Purpose: Store one row per lab sample.
-- Source: sample_submissions.csv after cleaning/standardization.
-- ============================================================
-- sample_id is the unique ID of the sample.
-- subject_id tells us which subject/person the sample belongs to.
-- collection_site_code tells us where the sample was collected.
-- collection_datetime is when the sample was collected.
-- received_datetime is when the lab received it.
-- source_file and source_row help us trace the original source.

CREATE TABLE sample (
    sample_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    collection_site_code TEXT,
    sample_type TEXT,
    collection_datetime TIMESTAMP,
    received_datetime TIMESTAMP,
    priority TEXT,
    consent_recorded BOOLEAN,
    intake_temperature_c NUMERIC,
    operator_notes TEXT,

    source_file TEXT,
    source_row INTEGER,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sample_site
-- This foreign key connects sample.collection_site_code to dim_site.site_code
-- It makes sure the sample uses a valid site code
--A sample cannot use a random site code unless that site exists in dim_site
        FOREIGN KEY (collection_site_code)
        REFERENCES dim_site(site_code),

    CONSTRAINT chk_sample_chronology
-- This check makes sure the sample is not received before it was collected
-- If one of the dates is missing, the check does not block the row
--Valid:collection_datetime = 10:00 received_datetime = 12:00
--Invalid: collection_datetime = 12:00 received_datetime = 10:00
        CHECK (
            collection_datetime IS NULL
            OR received_datetime IS NULL
            OR collection_datetime <= received_datetime
        )
);


-- ============================================================
-- Core table: assay_result
-- Purpose: Store lab measurement results.
-- Source: assay_results.csv, text reports, and PDF reports after cleaning.
-- Normalization reason: Results belong to samples and analytes.
-- ============================================================
-- Each result belongs to one sample.
-- Each result also belongs to one analyte/test.

-- result_id uniquely identifies the result.
-- sample_id tells which sample this result belongs to.
-- analyte_code tells which test/analyte was measured.
-- result_value is the measured value.
-- unit is the unit used in the source file.
-- qc_status stores quality control status.
-- review_status stores review/approval status.
-- version allows multiple versions of the same result.
-- is_current tells which version is the active one.
-- deleted_at is filled only if the result was deleted.

CREATE TABLE assay_result (
    result_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    analyte_code TEXT NOT NULL,
    result_value NUMERIC,
    unit TEXT,
    run_datetime TIMESTAMP,
    instrument_id TEXT,
    analyst TEXT,
    qc_status TEXT,
    review_status TEXT,
    approved_at TIMESTAMP,
    version INTEGER,
    is_current BOOLEAN,
    deleted_at TIMESTAMP,

    source_file TEXT,
    source_row INTEGER,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_assay_result_sample
-- This makes sure every assay result belongs to an existing sample.
        FOREIGN KEY (sample_id)
        REFERENCES sample(sample_id),

    CONSTRAINT fk_assay_result_analyte
-- This makes sure every assay result uses a valid analyte code.
        FOREIGN KEY (analyte_code)
        REFERENCES dim_analyte(analyte_code),

    CONSTRAINT chk_assay_result_non_negative
-- This check prevents negative result values.
-- If the result value is missing, the row is still allowed
        CHECK (
            result_value IS NULL
            OR result_value >= 0
        ),

    CONSTRAINT chk_deleted_result_not_current
-- If a result was deleted, it cannot be marked as current
--Invalid situation: deleted_at has a date & is_current = true
        CHECK (
            deleted_at IS NULL
            OR is_current IS NOT TRUE
        )
);


-- ============================================================
-- Core table: shipment
-- Purpose: Store shipment records from paginated JSON API files.
-- Normalization reason: Shipments are events related to samples.
-- ============================================================
-- This table stores shipment information for samples.
-- Each shipment belongs to one sample.
-- shipped_at is when the shipment was sent.
-- received_at is when the shipment arrived.
-- condition_temp_c stores the temperature during shipment.
-- status stores the shipment status.

CREATE TABLE shipment (
    shipment_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    courier TEXT,
    shipped_at TIMESTAMP,
    received_at TIMESTAMP,
    condition_temp_c NUMERIC,
    status TEXT,
    api_updated_at TIMESTAMP,

    source_file TEXT,
    source_page INTEGER,
    source_record_index INTEGER,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_shipment_sample
-- This makes sure every shipment belongs to an existing sample
        FOREIGN KEY (sample_id)
        REFERENCES sample(sample_id),

    CONSTRAINT chk_shipment_chronology
-- This check makes sure a shipment is not received before it was shipped
        CHECK (
            shipped_at IS NULL
            OR received_at IS NULL
            OR shipped_at <= received_at
        )
);


-- ============================================================
-- Core table: workflow_event
-- Purpose: Store sample workflow history.
-- Normalization reason: A sample can have many workflow events over time.
-- ============================================================
-- This table stores the history of what happened to a sample.
-- Example events: received, reviewed, approved, repeated, rejected.

CREATE TABLE workflow_event (
    event_id TEXT PRIMARY KEY,
    sample_id TEXT NOT NULL,
    event_status TEXT,
    event_timestamp TIMESTAMP,
    actor TEXT,
    message TEXT,

    source_file TEXT,
    source_row INTEGER,
    ingested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_workflow_event_sample
-- This makes sure every workflow event belongs to an existing sample.
        FOREIGN KEY (sample_id)
        REFERENCES sample(sample_id)
);


-- ============================================================
-- Audit table: validation_result
-- Purpose: Store validation outcomes for rows and fields.
-- Normalization reason: Validation results are separate audit events, not part of the business entity itself.
-- ============================================================
-- This table stores the result of validation checks.
-- It tells us if a row or field passed or failed a rule.
-- It is an audit table, so it stores checking history.

CREATE TABLE validation_result (
    validation_result_id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_record_id TEXT,
    source_field TEXT,
    is_valid BOOLEAN NOT NULL,
    severity TEXT,
    action TEXT,
    message TEXT,

    source_file TEXT,
    source_row INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_validation_result_rule
-- This connects each validation result to the rule that was checked.
        FOREIGN KEY (rule_id)
        REFERENCES validation_rule(rule_id)
);


-- ============================================================
-- Audit table: rejected_record
-- Purpose: Store records rejected or sent to review.
-- Normalization reason: Rejection information is audit data and should not be mixed with clean business tables.
-- ============================================================
-- It keeps the reason why the record was rejected.
-- raw_payload can store the original raw data.
-- This helps us debug data quality problems later.

CREATE TABLE rejected_record (
    rejected_record_id TEXT PRIMARY KEY,
    source_table TEXT,
    source_record_id TEXT,
    source_file TEXT,
    source_row INTEGER,
    source_sheet TEXT,
    source_page INTEGER,
    rule_id TEXT,
    severity TEXT,
    rejection_reason TEXT NOT NULL,
    raw_payload TEXT,
    run_id TEXT,
    rejected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_rejected_record_rule
-- This connects the rejected record to the rule that caused the rejection.
        FOREIGN KEY (rule_id)
        REFERENCES validation_rule(rule_id)
);


-- ============================================================
-- Indexes
-- Purpose: Support joins, filters, quality checks, and future feature queries.
-- Do not index every column.
-- Index columns used frequently in JOIN, WHERE, GROUP BY, and ORDER BY.
-- ============================================================
-- Create an index to make searches and joins faster on this column.

-- Makes it faster to find samples by site.
-- Also helps when joining sample with dim_site.
CREATE INDEX idx_sample_collection_site_code
ON sample(collection_site_code);

-- Makes it faster to find all samples for one subject.
CREATE INDEX idx_sample_subject_id
ON sample(subject_id);

-- Makes it faster to find all results for one sample.
CREATE INDEX idx_assay_result_sample_id
ON assay_result(sample_id);

-- Makes it faster to find results by analyte/test.
CREATE INDEX idx_assay_result_analyte_code
ON assay_result(analyte_code);

-- Makes it faster to find the current result for a sample and analyte.
CREATE INDEX idx_assay_result_current
ON assay_result(sample_id, analyte_code, is_current);

-- Makes it faster to find shipments for one sample
CREATE INDEX idx_shipment_sample_id
ON shipment(sample_id);

-- Makes it faster to filter shipments by status
CREATE INDEX idx_shipment_status
ON shipment(status);

-- Makes it faster to find workflow events for one sample
CREATE INDEX idx_workflow_event_sample_id
ON workflow_event(sample_id);

-- Makes it faster to sort or filter workflow events by date and time.
CREATE INDEX idx_workflow_event_timestamp
ON workflow_event(event_timestamp);

-- Makes it faster to find validation results for one rule
CREATE INDEX idx_validation_result_rule_id
ON validation_result(rule_id);

-- Makes it faster to find validation results for a specific source record
CREATE INDEX idx_validation_result_source
ON validation_result(source_table, source_record_id);

-- Makes it faster to find rejected records caused by one rule
CREATE INDEX idx_rejected_record_rule_id
ON rejected_record(rule_id);

-- Makes it faster to find rejected records from a specific source record.
CREATE INDEX idx_rejected_record_source
ON rejected_record(source_table, source_record_id);


-- ============================================================
-- View: sample_quality_summary_view
-- Purpose: Simplify future quality queries without immediately creating a denormalized physical table.
-- View vs denormalized table:
-- This view reads from normalized source tables.
-- If future queries become too complex or slow, this view can later become a physical denormalized table.
-- ============================================================
-- Create a view.
-- A view is a saved SELECT query.
-- It does not store new data like a table.
-- It shows a summary by reading the existing tables.

-- Select basic sample information.
-- Also include the site name from dim_site.
CREATE VIEW sample_quality_summary_view AS
SELECT
    s.sample_id,
    s.subject_id,
    s.collection_site_code,
    ds.site_name,
    s.sample_type,
    s.priority,
    s.collection_datetime,
    s.received_datetime,

-- Count how many assay results each sample has
-- DISTINCT avoids counting the same result more than once
    COUNT(DISTINCT ar.result_id) AS assay_result_count,

-- Count how many shipment records each sample has
    COUNT(DISTINCT sh.shipment_id) AS shipment_count,

-- Count how many workflow events each sample has.
    COUNT(DISTINCT we.event_id) AS workflow_event_count,

-- Check if any workflow message contains "retry" or "repeat".
-- LOWER makes the search case-insensitive.
-- If at least one message contains those words, return 1.
-- Otherwise return 0.
    MAX(
        CASE
            WHEN LOWER(we.message) LIKE '%retry%'
              OR LOWER(we.message) LIKE '%repeat%'
            THEN 1
            ELSE 0
        END
    ) AS has_retry_or_repeat_message

FROM sample s
-- LEFT JOIN keeps all samples
-- If matching site information exists, it adds it
-- If not, the sample still appears with empty site details
LEFT JOIN dim_site ds
    ON s.collection_site_code = ds.site_code
LEFT JOIN assay_result ar
    ON s.sample_id = ar.sample_id
LEFT JOIN shipment sh
    ON s.sample_id = sh.sample_id
LEFT JOIN workflow_event we
    ON s.sample_id = we.sample_id
-- GROUP BY creates one summary row per sample.
-- It is needed because we are using COUNT and MAX.
GROUP BY
    s.sample_id,
    s.subject_id,
    s.collection_site_code,
    ds.site_name,
    s.sample_type,
    s.priority,
    s.collection_datetime,
    s.received_datetime;