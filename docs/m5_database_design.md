# M5 Database Design

## Purpose

This document explains the database design for the Synthetic Lab Pipeline project.

The goal of M5 is to define a clean database structure that supports:

- normalized source-of-truth tables
- clear primary keys and foreign keys
- quality checks
- future reporting queries
- future feature engineering
- possible denormalized outputs if queries become too complex

The related SQL files are:

```text
sql/m5_database_schema.sql
sql/quality_checks.sql
```

---

## Main Design Idea

The database is designed with a normalized structure first.

This means that each table should store one main type of information.

For example:

- `sample` stores sample intake information
- `assay_result` stores lab measurement results
- `shipment` stores shipment events
- `workflow_event` stores workflow history
- `dim_site` stores site reference information
- `dim_analyte` stores analyte reference information
- `validation_rule` stores validation rule definitions
- `validation_result` stores validation outcomes
- `rejected_record` stores rejected or review records

The normalized tables are the source of truth.

---

## Why Normalization Is Used

Normalization helps avoid duplicated and inconsistent data.

For example, site information should not be repeated inside every sample row.

Instead of storing this repeatedly:

```text
sample_id | site_code | site_name | country | site_type
```

the design stores site information once in:

```text
dim_site
```

and the `sample` table references it through:

```text
collection_site_code
```

This keeps the schema cleaner and makes updates safer.

---

## Normalized Tables

### `dim_site`

Stores controlled site information.

Primary key:

```text
site_code
```

Used by:

```text
sample.collection_site_code
```

Relationship:

```text
dim_site 1 -> many sample
```

---

### `dim_analyte`

Stores controlled analyte information.

Primary key:

```text
analyte_code
```

Stores:

- analyte name
- canonical unit
- reference low value
- reference high value

Used by:

```text
assay_result.analyte_code
```

Relationship:

```text
dim_analyte 1 -> many assay_result
```

---

### `validation_rule`

Stores validation rule definitions.

Primary key:

```text
rule_id
```

Used by:

```text
validation_result.rule_id
rejected_record.rule_id
```

This makes validation and rejection results auditable.

---

### `sample`

Stores one row per lab sample.

Primary key:

```text
sample_id
```

Foreign key:

```text
collection_site_code -> dim_site.site_code
```

This table comes mainly from cleaned and standardized `sample_submissions.csv`.

Important rule:

```text
collection_datetime must not be after received_datetime
```

---

### `assay_result`

Stores lab measurement results.

Primary key:

```text
result_id
```

Foreign keys:

```text
sample_id -> sample.sample_id
analyte_code -> dim_analyte.analyte_code
```

Important rules:

```text
result_value must be non-negative
deleted records should not be current
```

This table supports checks for:

- orphan assay results
- duplicate current results
- reference range violations
- unit mismatches

---

### `shipment`

Stores shipment records from paginated JSON files.

Primary key:

```text
shipment_id
```

Foreign key:

```text
sample_id -> sample.sample_id
```

Important rule:

```text
shipped_at must not be after received_at
```

This table supports checks for:

- delayed shipments
- delivered shipments missing `received_at`

---

### `workflow_event`

Stores sample workflow history.

Primary key:

```text
event_id
```

Foreign key:

```text
sample_id -> sample.sample_id
```

A sample can have many workflow events.

This table is important because workflow messages may contain useful information such as:

```text
retry
repeat
```

---

### `validation_result`

Stores validation outcomes.

Primary key:

```text
validation_result_id
```

Foreign key:

```text
rule_id -> validation_rule.rule_id
```

This table is separated from business tables because validation results are audit information.

---

### `rejected_record`

Stores records rejected or sent to review.

Primary key:

```text
rejected_record_id
```

Foreign key:

```text
rule_id -> validation_rule.rule_id
```

This table keeps rejected data traceable.

It stores:

- source table
- source record ID
- source file
- source row
- rule ID
- severity
- rejection reason
- raw payload
- run ID

---

## Primary Keys

Primary keys uniquely identify one row.

Examples:

```text
sample.sample_id
assay_result.result_id
shipment.shipment_id
workflow_event.event_id
dim_site.site_code
dim_analyte.analyte_code
validation_rule.rule_id
```

Primary keys are important because every important record must be traceable.

---

## Foreign Keys

Foreign keys connect tables.

Main relationships:

```text
sample.collection_site_code -> dim_site.site_code
assay_result.sample_id -> sample.sample_id
assay_result.analyte_code -> dim_analyte.analyte_code
shipment.sample_id -> sample.sample_id
workflow_event.sample_id -> sample.sample_id
validation_result.rule_id -> validation_rule.rule_id
rejected_record.rule_id -> validation_rule.rule_id
```

Foreign keys help protect data integrity.

For example, an assay result should belong to an existing sample.

---

## Index Plan
Indexes are added to support common joins, filters, and quality checks

Indexes are useful on columns commonly used in:

- `JOIN`
- `WHERE`
- `GROUP BY`
- `ORDER BY`

Important indexes include:

- `sample.collection_site_code`
- `sample.subject_id`
- `assay_result.sample_id`
- `assay_result.analyte_code`
- `assay_result.sample_id + analyte_code + is_current`
- `shipment.sample_id`
- `shipment.status`
- `workflow_event.sample_id`
- `workflow_event.event_timestamp`
- `validation_result.rule_id`
- `validation_result.source_table + source_record_id`
- `rejected_record.rule_id`
- `rejected_record.source_table + source_record_id`

Indexes should not be added randomly to every column.

They help read performance, but too many indexes can slow down inserts and updates.


## Quality Checks

The file:

```text
sql/quality_checks.sql
```

contains SQL queries used to inspect data quality after records are loaded.

The checks include:
- orphan assay results
- duplicate current result versions
- detailed duplicate current result rows
- samples without workflow events
- current results outside reference range
- unit mismatches before reference-range comparison
- delayed shipments
- delivered shipments missing `received_at`

Some checks should return zero rows

Example:

```text
orphan assay results should return zero rows
```

Other checks may return rows for review

Example:

```text
current results outside reference range may exist and should be reviewed
```

## View Design

The schema includes:

```text
sample_quality_summary_view
```

A view is a saved query
It reads from normalized source tables and simplifies repeated joins

The view combines information from:
- `sample`
- `dim_site`
- `assay_result`
- `shipment`
- `workflow_event`

The view is useful for reporting and future feature exploration.

## View vs Denormalized Table
A view does not duplicate data
It uses the normalized source tables when queried

This is useful because:
- source tables remain the source of truth
- logic is centralized
- data is not copied unnecessarily

However, if the view becomes slow or too complex, it can later be converted into a denormalized physical table

---

## Denormalization Plan
Normalization is the default design choice, but it is not always the best final solution

Denormalization may be useful when:
- queries become too complicated
- too many joins are required
- reporting becomes slow
- ML feature generation needs one ready-to-use table
- the same joined dataset is used repeatedly

A future denormalized table could be:

```text
sample_quality_summary
```

or:

```text
sample_feature_table
```

This table could store precomputed values such as:
- assay result count
- shipment count
- workflow event count
- collection-to-received delay
- shipment transit hours
- retry/repeat message flag

The normalized tables would still remain the source of truth

## Why Not Denormalize Immediately
The project starts with normalization because the relationships are still important and the schema should remain auditable

Denormalizing too early can create problems:
- duplicated data
- stale values
- more refresh logic
- harder debugging
- unclear source of truth

For this reason, M5 uses a view first

A physical denormalized table can be added later only if there is a clear performance or usability need