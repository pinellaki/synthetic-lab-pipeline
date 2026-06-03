START PIPELINE DATABASE LOAD

1. Decide which database tool to use

   IF the task is local exploration, quick file inspection, or testing raw CSV/Parquet data:
       Use DuckDB.
       Reason:
           DuckDB is simple, local, and good for analytical queries on files.
           It does not require a running database server.

   ELSE IF the task is persistent storage, normalized database design, relational checks, or production-like loading:
       Use PostgreSQL.
       Reason:
           PostgreSQL supports primary keys, foreign keys, indexes, transactions,
           normalized schemas, and reliable multi-step loads.

   FOR this pipeline database load:
       Use PostgreSQL as the final target database.
       Optionally use DuckDB before PostgreSQL only for local exploration or data profiling.

2. Read database configuration

   Read database configuration from environment/configuration, not from hardcoded code.

   Get:
       database host
       database port
       database name
       database user
       database password
       database URL
       SQL logging option

   IF configuration is missing:
       Stop the load.
       Show a clear configuration error.
       Do not start inserting data.

   Credentials must come from:
       environment variables
       local .env file ignored by Git
       or a secret manager

   Credentials must NOT be:
       written directly inside Python files
       committed to GitHub
       copied into SQL scripts

3. Connect to PostgreSQL

   Open a database connection using the database configuration.

   IF the connection fails:
       Log the error.
       Stop the pipeline.
       Do not attempt the load.

   IF the connection succeeds:
       Continue to the load process.

4. Start transaction boundary

   Start one transaction for the load run.

   This means:
       Do not permanently save database changes immediately.
       Keep all inserts/updates temporary until the whole load succeeds.

   The transaction includes:
       loading dimensions
       loading samples
       loading assay results
       loading shipments
       loading workflow events
       saving validation results
       saving rejected records if needed

   Decision:
       IF this is a small/medium load:
           Use one transaction for the whole load run.

       IF this becomes a very large load in the future:
           Consider smaller transactions per logical batch,
           but still keep each batch consistent and retryable.

5. Load dimension/reference tables first

   Load dim_site first.
   Reason:
       sample records reference site codes.

   Load dim_analyte next.
   Reason:
       assay result records reference analyte codes.

   Load validation_rule next.
   Reason:
       validation results and rejected records may reference validation rules.

   For each dimension/reference row:
       Use parameterized INSERT or UPSERT query.

   Parameterization required here:
       site_code
       site_name
       country
       analyte_code
       analyte_name
       canonical_unit
       reference_low
       reference_high
       rule_id
       severity
       action

   DO NOT build SQL by concatenating values into strings.

Example logic:

FOR each site record:
    Execute parameterized INSERT/UPSERT into dim_site.

FOR each analyte record:
    Execute parameterized INSERT/UPSERT into dim_analyte.

FOR each validation rule:
    Execute parameterized INSERT/UPSERT into validation_rule.

6. Load sample records

   After dimensions are loaded, load samples.

   Reason:
       sample depends on dim_site through collection_site_code.
       assay_result, shipment, and workflow_event depend on sample.

   FOR each sample record:
       Standardize sample_id.
       Standardize dates.
       Standardize boolean fields if needed.
       Validate required fields.

       IF sample is valid:
           Insert sample into sample table using a parameterized query.

       ELSE:
           Create rejected_record.
           Insert rejected record using a parameterized query.
           Do not insert invalid sample into sample table.

   Parameterization required here:
       sample_id
       subject_id
       collection_site_code
       sample_type
       collection_datetime
       received_datetime
       priority
       consent_recorded
       intake_temperature_c
       source_file
       source_row
       run_id

7. Load assay result records

   Load assay results after samples.

   Reason:
       assay_result references sample through sample_id.
       assay_result references dim_analyte through analyte_code.

   FOR each assay result:
       Standardize sample_id.
       Standardize unit.
       Standardize dates.
       Standardize boolean is_current.
       Validate required fields.
       Validate result value is numeric.
       Validate result value is non-negative.

       IF assay result is valid and sample_id exists in sample:
           Insert assay result using a parameterized query.

       ELSE:
           Create rejected_record.
           Insert rejected record using a parameterized query.

   Parameterization required here:
       result_id
       sample_id
       analyte_code
       result_value
       unit
       run_datetime
       instrument_id
       analyst
       qc_status
       review_status
       approved_at
       version
       is_current
       deleted_at
       source_file
       source_row
       run_id

Decision:

IF assay_result.sample_id does not exist in sample:
    Do not insert it as a valid assay result.
    Reject it or send it to review.
    Reason:
        It would create an orphan assay result.

8. Load shipment records

   Load shipments after samples.

   Reason:
       shipment references sample through sample_id.

   FOR each shipment:
       Standardize sample_id.
       Standardize shipped_at and received_at dates.
       Validate required fields if rules exist.
       Validate temperature if provided.

       IF shipment is valid and sample_id exists:
           Insert shipment using a parameterized query.

       ELSE:
           Create rejected_record.
           Insert rejected record using a parameterized query.

   Parameterization required here:
       shipment_id
       sample_id
       courier
       shipped_at
       received_at
       condition_temp_c
       status
       api_updated_at
       source_file
       source_row
       run_id

9. Load workflow event records

   Load workflow events after samples.

   Reason:
       workflow_event references sample through sample_id.

   FOR each workflow event:
       Standardize sample_id.
       Standardize event timestamp.
       Validate required fields if rules exist.

       IF workflow event is valid and sample_id exists:
           Insert workflow event using a parameterized query.

       ELSE:
           Create rejected_record.
           Insert rejected record using a parameterized query.

   Parameterization required here:
       event_id
       sample_id
       event_status
       event_timestamp
       actor
       message
       source_file
       source_row
       run_id

10. Save validation results and rejected records

   FOR each validation check:
       Save the validation result if needed.

   FOR each rejected record:
       Save the rejected record.

   Reason:
       The pipeline must keep auditability.
       We need to know what failed, why it failed, where it came from,
       and which rule caused the issue.

   Parameterization required here:
       validation_result_id
       rule_id
       source_table
       source_record_id
       is_valid
       severity
       message
       action
       created_at

       rejected_record_id
       source_file
       source_record_id
       rule_id
       severity
       rejection_reason
       rejected_at
       run_id
       source_row
       source_sheet
       source_page

11. Run quality checks before final success

   Run SQL quality checks after loading.

   Checks include:
       orphan assay results
       duplicate current assay results
       samples without workflow events
       results outside reference range
       unit mismatches
       delayed shipments
       delivered shipments missing received_at

   IF critical quality checks fail:
       Roll back the transaction.
       Mark load as failed.
       Log the reason.
       Do not leave the database half-loaded.

   IF only review-level checks return rows:
       Decide based on business rules:
           either allow load and mark records for review
           or fail the load if the issue is critical.

12. Commit or rollback transaction

   IF all required load steps succeed:
       Commit the transaction.
       Mark the load run as successful.
       Log success.

   ELSE IF any critical step fails:
       Roll back the transaction.
       Mark the load run as failed.
       Log the error.
       Keep enough information to debug and retry.

   Failure behavior:
       No partial load should be treated as successful.
       The database should not contain only half of the loaded data.
       The pipeline should be safe to rerun after fixing the problem.

13. Close resources

   Close database cursor.
   Close database connection.
   Close open files if any.

   Log:
       load status
       number of inserted records
       number of rejected records
       number of reviewed records
       error message if failed

Final load order summary
1. dim_site
2. dim_analyte
3. validation_rule
4. sample
5. assay_result
6. shipment
7. workflow_event
8. validation_result
9. rejected_record
10. quality checks
11. commit if successful / rollback if failed

Where parameterization is required
Parameterized queries are required for every SQL statement that uses values from:

- source files
- user input
- configuration values
- Python variables
- validation results
- rejected records
- IDs
- dates
- numeric values
- statuses
- messages

Examples:

INSERT INTO sample (...) VALUES (?, ?, ?, ...)
INSERT INTO assay_result (...) VALUES (?, ?, ?, ...)
SELECT * FROM sample WHERE sample_id = ?
UPDATE load_run SET status = ? WHERE run_id = ?