-- M5 quality checks for Synthetic Lab Pipeline
-- Purpose: Validate relationships, duplicates, reference ranges, and shipment delays.

-- Aliases are short names for tables. They make the query shorter and easier to read.

-- This file does not create or change data.
-- It only reads the database and finds possible data quality problems.
-- Queries expected to return zero rows are checks for errors.
-- If they return rows, those rows should be investigated.
-- Some checks may return rows normally, but those rows should still be reviewed.


-- ============================================================
-- Check 1: Orphan assay results
-- Business question: Do all assay results belong to an existing sample?
-- Expected result: Zero rows.
-- ============================================================
--Are there assay results that point to a sample_id that does not exist in the sample table?
-- We start from assay_result because we want to inspect all results
-- LEFT JOIN keeps all assay results, even if the related sample is missing
-- If s.sample_id is NULL, it means no matching sample was found
-- If rows are returned, those assay results are orphan records

-- Show the key information needed to investigate the bad assay result.
-- source_file and source_row help us find where the wrong data came from.
SELECT
    ar.result_id,
    ar.sample_id,
    ar.analyte_code,
    ar.result_value,
    ar.source_file,
    ar.source_row
-- Read data from the assay_result table.
FROM assay_result ar
-- Try to find the matching sample for each assay result. Match using sample_id
LEFT JOIN sample s
    ON ar.sample_id = s.sample_id
-- Keep only assay results where no matching sample was found
WHERE s.sample_id IS NULL;


-- ============================================================
-- Check 2: Duplicate current result versions
-- Business question: Does each sample/analyte have only one current result?
-- Expected result: Zero rows
-- ============================================================
--For the same sample and same analyte, is there more than one result marked as current?
-- Only current results are considered.
-- GROUP BY creates one group for each sample_id and analyte_code.
-- COUNT(*) counts how many current results exist in each group.
-- HAVING COUNT(*) > 1 keeps only duplicate current results.

-- Show the sample, the analyte, and how many current results exist for that pair
SELECT
    sample_id,
    analyte_code,
    COUNT(*) AS current_result_count
FROM assay_result
-- Only check rows marked as the current active result
WHERE is_current = true
-- Group results by sample and analyte
-- This lets us count how many current rows exist for each pair
GROUP BY
    sample_id,
    analyte_code
-- Return only sample/analyte pairs with more than one current result
HAVING COUNT(*) > 1;


-- ============================================================
-- Check 2b: Detailed duplicate current result rows
-- Purpose: Show the actual rows involved in duplicate current conflicts
-- ============================================================
-- First, find sample/analyte pairs that have more than one current result
-- Store those pairs temporarily in duplicate_current
-- Then join back to assay_result to show the actual duplicate rows
-- This helps us see result_id, version, value, unit, and deleted_at
-- Expected result: zero rows.
-- If rows are returned, we need to decide which result should remain current

-- Create a temporary result called duplicate_current.
-- It contains only sample/analyte pairs with duplicate current results.
WITH duplicate_current AS (
-- Find sample/analyte pairs where more than one row is marked as current.
    SELECT
        sample_id,
        analyte_code
    FROM assay_result
    WHERE is_current = true
    GROUP BY
        sample_id,
        analyte_code
    HAVING COUNT(*) > 1
)
SELECT
    ar.result_id,
    ar.sample_id,
    ar.analyte_code,
    ar.version,
    ar.is_current,
    ar.deleted_at,
    ar.result_value,
    ar.unit
FROM assay_result ar
JOIN duplicate_current dc
-- Match rows using both sample_id and analyte_code
-- Both columns are needed because the duplicate is defined by this pair
    ON ar.sample_id = dc.sample_id
   AND ar.analyte_code = dc.analyte_code
-- Show only the rows currently marked as active/current.
WHERE ar.is_current = true
ORDER BY
    ar.sample_id,
    ar.analyte_code,
    ar.version;


-- ============================================================
-- Check 3: Samples without workflow events
-- Business question: Does every sample have at least one workflow event?
-- Expected result: Zero rows, unless there is a valid business explanation
-- ============================================================
--Does every sample have at least one workflow event?
-- Check if there are samples with no workflow history
-- We start from sample because we want to inspect all samples
-- LEFT JOIN keeps all samples, even if they have no workflow_event
-- If we.event_id is NULL, no workflow event was found for that sample
-- Expected result: zero rows, unless there is a valid business reason

SELECT
    s.sample_id,
    s.subject_id,
    s.collection_site_code,
    s.received_datetime,
    s.source_file,
    s.source_row
FROM sample s
-- Try to find workflow events connected to each sample
LEFT JOIN workflow_event we
    ON s.sample_id = we.sample_id
-- Keep only samples where no workflow event exists
WHERE we.event_id IS NULL;


-- ============================================================
-- Check 4: Current results outside reference range
-- Business question: Which current assay results are outside the analyte reference range?
-- Expected result: Rows may exist; they should be reviewed
-- ============================================================
--Which current lab results are lower or higher than the normal reference range?
-- Check current assay results that are outside the analyte reference range
-- Join assay_result with dim_analyte to get the official reference range
-- Only current results are checked
-- Only compare values when the result unit matches the canonical analyte unit
-- Return rows where result_value is below reference_low or above reference_high

SELECT
    ar.result_id,
    ar.sample_id,
    ar.analyte_code,
    da.analyte_name,
    ar.result_value,
    ar.unit,
    da.reference_low,
    da.reference_high,
    da.canonical_unit,
    ar.qc_status,
    ar.run_datetime
-- Connect each assay result to its analyte reference information
-- This gives us the analyte name, canonical unit, and reference range
FROM assay_result ar
JOIN dim_analyte da
    ON ar.analyte_code = da.analyte_code
-- Only check the active/current version of each result
WHERE ar.is_current = true
-- Compare values only when the result unit matches the official unit
-- This prevents wrong comparisons between different units
  AND ar.unit = da.canonical_unit
-- Return results that are lower than the minimum normal value or higher than the maximum normal value
  AND (
        ar.result_value < da.reference_low
        OR ar.result_value > da.reference_high
      );


-- ============================================================
-- Check 4b: Unit mismatches before reference-range comparison
-- Business question: Do assay result units match the canonical analyte unit?
-- Expected result: Zero rows after cleaning
-- ============================================================
-- Are there assay results where the result unit is different from the official unit?
-- Check if assay result units match the official analyte units.
-- Join assay_result with dim_analyte to get the canonical unit.
-- <> means "not equal".
-- Return rows where the result unit is different from the canonical unit.
-- Expected result: zero rows after cleaning.

SELECT
    ar.result_id,
    ar.sample_id,
    ar.analyte_code,
    ar.unit AS result_unit,
    da.canonical_unit
FROM assay_result ar
JOIN dim_analyte da
    ON ar.analyte_code = da.analyte_code
--result unit is different from canonical unit
-- <> not equal
WHERE ar.unit <> da.canonical_unit;


-- ============================================================
-- Check 5: Delayed shipments
-- Business question: Which shipments are marked delayed or took more than 24 hours?
-- Expected result: Rows may exist; they should be reviewed
-- ============================================================
-- Calculate how many hours passed between shipped_at and received_at
-- received_at - shipped_at gives the time difference
-- EXTRACT(EPOCH FROM ...) converts the difference into seconds
-- Dividing by 3600 converts seconds into hours. 1 hour = 3600 seconds. So, seconds / 3600 = hours
-- The result column is called transit_hours

SELECT
    shipment_id,
    sample_id,
    courier,
    shipped_at,
    received_at,
    condition_temp_c,
    status,
    api_updated_at,
    EXTRACT(EPOCH FROM (received_at - shipped_at)) / 3600 AS transit_hours
FROM shipment
-- Return shipments already marked as delayed
WHERE status = 'delayed'
-- Also return shipments where both dates exist and the transit time is more than 24 hours
   OR (
-- We check that both timestamps exist before calculating the time difference
-- This avoids calculating with missing dates
        received_at IS NOT NULL
        AND shipped_at IS NOT NULL
        AND EXTRACT(EPOCH FROM (received_at - shipped_at)) / 3600 > 24
      );


-- ============================================================
-- Check 5b: Delivered shipments missing received_at
-- Business question: Are any delivered shipments missing a received timestamp?
-- Expected result: Zero rows
-- ============================================================
--Are there shipments marked as delivered but missing the received_at timestamp?
-- Check delivered shipments that do not have a received_at timestamp
-- If status is 'delivered', received_at should normally be filled
-- If rows are returned, the shipment status or received_at value may be wrong

SELECT
    shipment_id,
    sample_id,
    courier,
    shipped_at,
    received_at,
    status
FROM shipment
WHERE status = 'delivered'
  AND received_at IS NULL;