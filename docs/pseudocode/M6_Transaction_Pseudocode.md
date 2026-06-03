Start pipeline run and create run_id.

Open database connection.

Begin transaction.

Load dimension/reference tables:
- dim_site
- dim_subject
- dim_analyte

Load core trusted tables:
- sample
- assay_result
- workflow_event
- shipment

Load audit tables:
- rejected_record
- validation_warning
- pipeline_run_log updates

Run critical SQL checks:
- orphan assay results
- duplicate current result versions
- missing required workflow events if required
- unit mismatches
- leakage check for feature table if features are created

If critical checks return zero blocking errors:
- commit transaction
- mark pipeline run as success

If critical checks return blocking errors:
- rollback transaction
- mark pipeline run as failed
- save or report error details outside the rolled-back transaction if needed

Close database connection.