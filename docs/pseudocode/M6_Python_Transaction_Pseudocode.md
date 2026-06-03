Try to load everything.
If anything critical fails, undo everything.

try:
    begin_transaction()

    load_dim_site()
    load_dim_subject()
    load_dim_analyte()
    load_sample()
    load_assay_result()
    load_workflow_event()
    load_shipment()

    run_critical_quality_checks()

    commit_transaction()

except Exception:
    rollback_transaction()
    log_failure()
    raise