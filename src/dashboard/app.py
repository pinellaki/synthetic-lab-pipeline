"""Streamlit frontend for the Synthetic Lab Pipeline governance dashboard.

The dashboard communicates with the existing FastAPI backend.

It contains three areas:

1. accepted laboratory and business data
2. validation, rejection, lineage, and issue-resolution governance
3. dashboard and API documentation

Streamlit does not connect directly to PostgreSQL. It reads and updates data
through FastAPI endpoints.
"""

from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


DEFAULT_API_URL = "http://127.0.0.1:8000"

RESOLUTION_STATUSES = [
    "open",
    "corrected",
    "resolved",
    "dismissed",
]


st.set_page_config(
    page_title="Synthetic Lab Governance Dashboard",
    page_icon="🧪",
    layout="wide",
)


@st.cache_data(ttl=30)
def fetch_api_data(
    api_base_url: str,
    endpoint: str,
) -> Any:
    """Read JSON data from one FastAPI endpoint."""
    response = requests.get(
        f"{api_base_url.rstrip('/')}{endpoint}",
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


def patch_api_data(
    api_base_url: str,
    endpoint: str,
    payload: dict[str, Any],
) -> Any:
    """Send one PATCH request to FastAPI."""
    response = requests.patch(
        f"{api_base_url.rstrip('/')}{endpoint}",
        json=payload,
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


def empty_string_to_none(value: str) -> str | None:
    """Convert empty or whitespace-only text into None."""
    cleaned_value = value.strip()

    if cleaned_value == "":
        return None

    return cleaned_value


def show_api_error(error: Exception) -> None:
    """Display a readable FastAPI connection or request error."""
    st.error(
        "The dashboard could not communicate with FastAPI. "
        "Make sure the FastAPI server is running with:\n\n"
        "`python -m uvicorn src.main:app --reload`"
    )

    with st.expander("Technical error details"):
        st.code(str(error))


def create_overview_metrics(overview: dict[str, Any]) -> None:
    """Display the main database and validation counters."""
    first_row = st.columns(4)

    first_row[0].metric(
        label="Accepted samples",
        value=overview["samples"],
    )
    first_row[1].metric(
        label="Accepted assay results",
        value=overview["assay_results"],
    )
    first_row[2].metric(
        label="Accepted shipments",
        value=overview["shipments"],
    )
    first_row[3].metric(
        label="Workflow events",
        value=overview["workflow_events"],
    )

    second_row = st.columns(4)

    second_row[0].metric(
        label="Validation checks",
        value=overview["validation_results"],
    )
    second_row[1].metric(
        label="Passed validations",
        value=overview["passed_validations"],
    )
    second_row[2].metric(
        label="Failed validations",
        value=overview["failed_validations"],
    )
    second_row[3].metric(
        label="Validation pass rate",
        value=f'{overview["validation_pass_rate"]:.2f}%',
    )


def show_data_overview(api_base_url: str) -> None:
    """Render the accepted laboratory-data area."""
    st.header("Laboratory data overview")

    st.write(
        "This area shows the valid records that completed the pipeline and "
        "were stored in PostgreSQL."
    )

    try:
        overview = fetch_api_data(
            api_base_url,
            "/dashboard/overview",
        )
        lab_results = fetch_api_data(
            api_base_url,
            "/dashboard/lab-results",
        )
        samples = fetch_api_data(
            api_base_url,
            "/dashboard/samples",
        )

    except requests.RequestException as error:
        show_api_error(error)
        return

    create_overview_metrics(overview)

    st.divider()

    st.subheader("Assay results by analyte")

    lab_results_dataframe = pd.DataFrame(lab_results)

    if lab_results_dataframe.empty:
        st.info("No analyte information is available.")
    else:
        analyte_count_chart = px.bar(
            lab_results_dataframe,
            x="analyte_code",
            y="result_count",
            hover_data=[
                "analyte_name",
                "canonical_unit",
                "average_value",
                "minimum_value",
                "maximum_value",
            ],
            labels={
                "analyte_code": "Analyte",
                "result_count": "Accepted results",
            },
            title="Accepted result count by analyte",
        )

        st.plotly_chart(
            analyte_count_chart,
            use_container_width=True,
        )

        st.dataframe(
            lab_results_dataframe[
                [
                    "analyte_code",
                    "analyte_name",
                    "canonical_unit",
                    "result_count",
                    "average_value",
                    "minimum_value",
                    "maximum_value",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "ALT appears with zero accepted results because it is configured "
            "in the analyte reference table, but its fake source result did "
            "not pass validation."
        )

    st.divider()

    st.subheader("Sample-level details")

    samples_dataframe = pd.DataFrame(samples)

    if samples_dataframe.empty:
        st.info("No accepted sample information is available.")
        return

    sample_counts_dataframe = samples_dataframe[
        [
            "sample_id",
            "assay_result_count",
            "shipment_count",
            "workflow_event_count",
        ]
    ].melt(
        id_vars="sample_id",
        var_name="record_type",
        value_name="record_count",
    )

    sample_chart = px.bar(
        sample_counts_dataframe,
        x="sample_id",
        y="record_count",
        color="record_type",
        barmode="group",
        labels={
            "sample_id": "Sample",
            "record_count": "Related records",
            "record_type": "Record type",
        },
        title="Related records by accepted sample",
    )

    st.plotly_chart(
        sample_chart,
        use_container_width=True,
    )

    st.dataframe(
        samples_dataframe,
        use_container_width=True,
        hide_index=True,
    )


def show_validation_rule_section(
    validation_rules: list[dict[str, Any]],
) -> None:
    """Render validation metrics grouped by rule."""
    st.subheader("Validation results by rule")

    rules_dataframe = pd.DataFrame(validation_rules)

    if rules_dataframe.empty:
        st.info("No validation-rule metrics are available.")
        return

    rule_chart_dataframe = rules_dataframe[
        [
            "rule_id",
            "passed_checks",
            "failed_checks",
        ]
    ].melt(
        id_vars="rule_id",
        var_name="validation_status",
        value_name="check_count",
    )

    rule_chart = px.bar(
        rule_chart_dataframe,
        x="rule_id",
        y="check_count",
        color="validation_status",
        barmode="group",
        labels={
            "rule_id": "Validation rule",
            "check_count": "Number of checks",
            "validation_status": "Validation status",
        },
        title="Passed and failed checks by validation rule",
    )

    st.plotly_chart(
        rule_chart,
        use_container_width=True,
    )

    st.dataframe(
        rules_dataframe,
        use_container_width=True,
        hide_index=True,
    )


def show_severity_and_lineage_section(
    validation_severity: list[dict[str, Any]],
    lineage: list[dict[str, Any]],
) -> None:
    """Render failure-severity and pipeline-lineage charts."""
    severity_column, lineage_column = st.columns(2)

    with severity_column:
        st.subheader("Failed checks by severity")

        severity_dataframe = pd.DataFrame(validation_severity)

        if severity_dataframe.empty:
            st.info("No failed validation severity data is available.")
        else:
            severity_chart = px.pie(
                severity_dataframe,
                names="severity",
                values="failed_checks",
                title="Distribution of failed checks",
            )

            st.plotly_chart(
                severity_chart,
                use_container_width=True,
            )

    with lineage_column:
        st.subheader("Pipeline lineage")

        lineage_dataframe = pd.DataFrame(lineage)

        if lineage_dataframe.empty:
            st.info("No lineage data is available.")
        else:
            lineage_chart = px.bar(
                lineage_dataframe,
                x="record_count",
                y="stage",
                orientation="h",
                hover_data=["explanation"],
                labels={
                    "record_count": "Records or checks",
                    "stage": "Pipeline stage",
                },
                title="Data movement through the pipeline",
            )

            st.plotly_chart(
                lineage_chart,
                use_container_width=True,
            )

    lineage_dataframe = pd.DataFrame(lineage)

    if not lineage_dataframe.empty:
        with st.expander("View lineage stage explanations"):
            st.dataframe(
                lineage_dataframe,
                use_container_width=True,
                hide_index=True,
            )


def show_resolution_status_section(
    resolution_status: list[dict[str, Any]],
) -> None:
    """Render rejected-record issue counts by resolution status."""
    st.subheader("Issue-resolution status")

    resolution_dataframe = pd.DataFrame(resolution_status)

    if resolution_dataframe.empty:
        st.info("No rejected-record resolution information is available.")
        return

    resolution_chart = px.bar(
        resolution_dataframe,
        x="resolution_status",
        y="issue_count",
        labels={
            "resolution_status": "Issue status",
            "issue_count": "Number of issues",
        },
        title="Rejected-record issues by resolution status",
    )

    st.plotly_chart(
        resolution_chart,
        use_container_width=True,
    )

    st.dataframe(
        resolution_dataframe,
        use_container_width=True,
        hide_index=True,
    )


def show_rejected_record_table(
    rejected_dataframe: pd.DataFrame,
) -> None:
    """Display rejected records with rule and status filters."""
    st.subheader("Rejected-record details")

    if rejected_dataframe.empty:
        st.success("No rejected records are currently stored.")
        return

    filter_columns = st.columns(2)

    available_rules = sorted(
        rejected_dataframe["rule_id"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    available_statuses = sorted(
        rejected_dataframe["resolution_status"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    selected_rules = filter_columns[0].multiselect(
        "Filter by validation rule",
        options=available_rules,
        default=available_rules,
    )

    selected_statuses = filter_columns[1].multiselect(
        "Filter by issue status",
        options=available_statuses,
        default=available_statuses,
    )

    filtered_rejections = rejected_dataframe.copy()

    if selected_rules:
        filtered_rejections = filtered_rejections[
            filtered_rejections["rule_id"].isin(selected_rules)
        ]
    else:
        filtered_rejections = filtered_rejections.iloc[0:0]

    if selected_statuses:
        filtered_rejections = filtered_rejections[
            filtered_rejections["resolution_status"].isin(
                selected_statuses
            )
        ]
    else:
        filtered_rejections = filtered_rejections.iloc[0:0]

    visible_columns = [
        "rejected_record_id",
        "source_table",
        "source_record_id",
        "source_file",
        "source_row",
        "rule_id",
        "severity",
        "rejection_reason",
        "resolution_status",
        "corrected_value",
        "resolution_note",
        "resolved_by",
        "resolved_at",
    ]

    st.dataframe(
        filtered_rejections[visible_columns],
        use_container_width=True,
        hide_index=True,
    )


def show_issue_resolution_form(
    api_base_url: str,
    rejected_dataframe: pd.DataFrame,
) -> None:
    """Render the form used to update one rejected-record issue."""
    st.subheader("Update an issue")

    if rejected_dataframe.empty:
        st.info("There are no rejected-record issues to update.")
        return

    issue_options: dict[str, str] = {}

    for _, row in rejected_dataframe.iterrows():
        source_record_id = row.get("source_record_id")

        if pd.isna(source_record_id) or source_record_id is None:
            source_record_id = "missing ID"

        label = (
            f'{row["rule_id"]} | {source_record_id} | '
            f'row {row["source_row"]} | {row["resolution_status"]}'
        )

        issue_options[label] = row["rejected_record_id"]

    selected_label = st.selectbox(
        "Select a rejected-record issue",
        options=list(issue_options.keys()),
    )

    selected_id = issue_options[selected_label]

    selected_rows = rejected_dataframe[
        rejected_dataframe["rejected_record_id"] == selected_id
    ]

    if selected_rows.empty:
        st.error("The selected rejected record could not be found.")
        return

    selected_row = selected_rows.iloc[0]

    current_status = str(selected_row["resolution_status"])

    if current_status not in RESOLUTION_STATUSES:
        current_status = "open"

    current_corrected_value = selected_row.get("corrected_value")
    current_resolution_note = selected_row.get("resolution_note")
    current_resolved_by = selected_row.get("resolved_by")

    if pd.isna(current_corrected_value):
        current_corrected_value = ""

    if pd.isna(current_resolution_note):
        current_resolution_note = ""

    if pd.isna(current_resolved_by):
        current_resolved_by = ""

    st.caption(
        f'Failure reason: {selected_row["rejection_reason"]}'
    )

    with st.form("issue_resolution_form"):
        new_status = st.selectbox(
            "Resolution status",
            options=RESOLUTION_STATUSES,
            index=RESOLUTION_STATUSES.index(current_status),
        )

        corrected_value = st.text_input(
            "Corrected value",
            value=str(current_corrected_value),
            help=(
                "Optional. Enter the corrected source value when the issue "
                "was fixed by changing a value."
            ),
        )

        resolution_note = st.text_area(
            "Resolution note",
            value=str(current_resolution_note),
            help="Explain how the issue was handled.",
        )

        resolved_by = st.text_input(
            "Resolved by",
            value=str(current_resolved_by),
            help="Person or process responsible for the update.",
        )

        submitted = st.form_submit_button(
            "Save issue update"
        )

    if not submitted:
        return

    payload = {
        "resolution_status": new_status,
        "corrected_value": empty_string_to_none(
            corrected_value
        ),
        "resolution_note": empty_string_to_none(
            resolution_note
        ),
        "resolved_by": empty_string_to_none(
            resolved_by
        ),
    }

    try:
        updated_issue = patch_api_data(
            api_base_url=api_base_url,
            endpoint=(
                "/dashboard/rejected-records/"
                f"{selected_id}/resolution"
            ),
            payload=payload,
        )

    except requests.RequestException as error:
        show_api_error(error)
        return

    st.success(
        "Issue updated successfully: "
        f'{updated_issue["resolution_status"]}'
    )

    st.cache_data.clear()
    st.rerun()


def show_governance_dashboard(api_base_url: str) -> None:
    """Render validation, rejection, lineage, and resolution information."""
    st.header("Validation and data-governance overview")

    st.write(
        "This area tracks what happened while data moved through the "
        "pipeline: checks performed, failed rules, accepted records, "
        "rejection reasons, and issue-resolution status."
    )

    try:
        overview = fetch_api_data(
            api_base_url,
            "/dashboard/overview",
        )
        validation_rules = fetch_api_data(
            api_base_url,
            "/dashboard/validation-rules",
        )
        validation_severity = fetch_api_data(
            api_base_url,
            "/dashboard/validation-severity",
        )
        rejected_records = fetch_api_data(
            api_base_url,
            "/dashboard/rejected-records",
        )
        resolution_status = fetch_api_data(
            api_base_url,
            "/dashboard/resolution-status",
        )
        lineage = fetch_api_data(
            api_base_url,
            "/dashboard/lineage",
        )

    except requests.RequestException as error:
        show_api_error(error)
        return

    first_metric_row = st.columns(4)

    first_metric_row[0].metric(
        label="Total validation checks",
        value=overview["validation_results"],
    )
    first_metric_row[1].metric(
        label="Passed checks",
        value=overview["passed_validations"],
    )
    first_metric_row[2].metric(
        label="Failed checks",
        value=overview["failed_validations"],
    )
    first_metric_row[3].metric(
        label="Rejected audit entries",
        value=overview["rejected_records"],
    )

    second_metric_row = st.columns(2)

    second_metric_row[0].metric(
        label="Open issues",
        value=overview["open_issues"],
    )
    second_metric_row[1].metric(
        label="Handled issues",
        value=overview["resolved_issues"],
        help="Corrected, resolved, or dismissed issues.",
    )

    st.divider()

    show_validation_rule_section(validation_rules)

    st.divider()

    show_severity_and_lineage_section(
        validation_severity=validation_severity,
        lineage=lineage,
    )

    st.divider()

    show_resolution_status_section(resolution_status)

    st.divider()

    rejected_dataframe = pd.DataFrame(rejected_records)

    show_rejected_record_table(rejected_dataframe)

    st.divider()

    show_issue_resolution_form(
        api_base_url=api_base_url,
        rejected_dataframe=rejected_dataframe,
    )


def show_documentation(api_base_url: str) -> None:
    """Render the dashboard documentation page."""
    st.header("Dashboard documentation")

    try:
        documentation = fetch_api_data(
            api_base_url,
            "/dashboard/documentation",
        )

    except requests.RequestException as error:
        show_api_error(error)
        return

    st.subheader(documentation["title"])

    st.write(documentation["purpose"])

    st.info(f'Data source: {documentation["data_source"]}')

    first_column, second_column = st.columns(2)

    with first_column:
        st.markdown("### Laboratory-data area")

        for item in documentation["data_area"]:
            st.markdown(f"- {item}")

    with second_column:
        st.markdown("### Governance area")

        for item in documentation["governance_area"]:
            st.markdown(f"- {item}")

    st.markdown("### What data lineage means")

    st.write(documentation["lineage_definition"])

    st.markdown("### What issue-resolution tracking means")

    st.write(documentation["resolution_definition"])

    st.markdown("### Application flow")

    st.code(
        """
PostgreSQL database
        ↓
FastAPI dashboard endpoints
        ↓
Streamlit dashboard
        ↓
Plotly charts, filters, details, and issue updates
        """.strip()
    )

    st.markdown("### Main FastAPI endpoints")

    endpoint_rows = [
        {
            "Method": "GET",
            "Endpoint": "/dashboard/overview",
            "Purpose": "High-level data, validation, and issue counters",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/lab-results",
            "Purpose": "Assay-result summaries by analyte",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/samples",
            "Purpose": "Accepted sample-level details",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/validation-rules",
            "Purpose": "Passed and failed checks by rule",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/validation-severity",
            "Purpose": "Failed checks grouped by severity",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/rejected-records",
            "Purpose": "Rejected records and resolution details",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/resolution-status",
            "Purpose": "Issue counts grouped by resolution status",
        },
        {
            "Method": "PATCH",
            "Endpoint": (
                "/dashboard/rejected-records/"
                "{rejected_record_id}/resolution"
            ),
            "Purpose": "Update one rejected-record issue",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/lineage",
            "Purpose": "Data movement and issue-lifetime metrics",
        },
        {
            "Method": "GET",
            "Endpoint": "/dashboard/documentation",
            "Purpose": "Documentation content for this page",
        },
    ]

    st.dataframe(
        pd.DataFrame(endpoint_rows),
        use_container_width=True,
        hide_index=True,
    )


def main() -> None:
    """Render the complete Streamlit governance dashboard."""
    st.title("Synthetic Lab Pipeline Governance Dashboard")

    st.caption(
        "Visualization of accepted laboratory data, validation outcomes, "
        "rejected records, issue resolution, and pipeline lineage."
    )

    with st.sidebar:
        st.header("Dashboard settings")

        api_base_url = st.text_input(
            "FastAPI base URL",
            value=DEFAULT_API_URL,
        )

        if st.button("Refresh dashboard data"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        st.markdown(
            """
            **Required backend command**

            `python -m uvicorn src.main:app --reload`
            """
        )

        st.markdown(
            """
            **FastAPI documentation**

            `http://127.0.0.1:8000/docs`
            """
        )

    data_tab, governance_tab, documentation_tab = st.tabs(
        [
            "Laboratory data",
            "Governance and lineage",
            "Documentation",
        ]
    )

    with data_tab:
        show_data_overview(api_base_url)

    with governance_tab:
        show_governance_dashboard(api_base_url)

    with documentation_tab:
        show_documentation(api_base_url)


if __name__ == "__main__":
    main()