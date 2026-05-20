\# M5 Database Design



\## Purpose



This document explains the database design for the Synthetic Lab Pipeline project



The goal of M5 is to define a clean database structure that supports:



\- normalized source-of-truth tables

\- clear primary keys and foreign keys

\- quality checks

\- future reporting queries

\- future feature engineering

\- possible denormalized outputs if queries become too complex



The related SQL files are:



```text

sql/m5\_database\_schema.sql

sql/quality\_checks.sql



\## Main Design Idea

The database is designed with a normalized structure first

This means that each table should store one main type of information



For example:

\-sample stores sample intake information

\-assay\_result stores lab measurement results

\-shipment stores shipment events

\-workflow\_event stores workflow history

\-dim\_site stores site reference information

\-dim\_analyte stores analyte reference information

\-validation\_rule stores validation rule definitions

\-validation\_result stores validation outcomes

\-rejected\_record stores rejected or review records



The normalized tables are the source of truth



\## Why Normalization Is Used

Normalization helps avoid duplicated and inconsistent data



For example, site information should not be repeated inside every sample row



Instead of storing this repeatedly:



sample\_id | site\_code | site\_name | country | site\_type



the design stores site information once in:

dim\_site



and the sample table references it through:

collection\_site\_code



This keeps the schema cleaner and makes updates safer



\## Normalized Tables



\### dim\_site

Stores controlled site information.



Primary key:

site\_code



Used by:

sample.collection\_site\_code



Relationship:

dim\_site 1 -> many sample



\### dim\_analyte

Stores controlled analyte information.



Primary key:

analyte\_code



Stores:

\-analyte name

\-canonical unit

\-reference low value

\-reference high value



Used by:

assay\_result.analyte\_code



Relationship:

dim\_analyte 1 -> many assay\_result



\### validation\_rule

Stores validation rule definitions



Primary key:

rule\_id



Used by:

validation\_result.rule\_id

rejected\_record.rule\_id



This makes validation and rejection results auditable



\### sample

Stores one row per lab sample.



Primary key:

sample\_id



Foreign key:

collection\_site\_code -> dim\_site.site\_code



This table comes mainly from cleaned and standardized sample\_submissions.csv.



Important rule:

collection\_datetime must not be after received\_datetime



\### assay\_result

Stores lab measurement results.



Primary key:

result\_id



Foreign keys:

sample\_id -> sample.sample\_id

analyte\_code -> dim\_analyte.analyte\_code



Important rules:

result\_value must be non-negative

deleted records should not be current



This table supports checks for:

\-orphan assay results

\-duplicate current results

\-reference range violations

\-unit mismatches



\### shipment

Stores shipment records from paginated JSON files.



Primary key:

shipment\_id



Foreign key:

sample\_id -> sample.sample\_id



Important rule:

shipped\_at must not be after received\_at



This table supports checks for:

delayed shipments

delivered shipments missing received\_at



\### workflow\_event

Stores sample workflow history.



Primary key:

event\_id



Foreign key:

sample\_id -> sample.sample\_id



A sample can have many workflow events.



This table is important because workflow messages may contain useful information such as:

retry

repeat



\### validation\_result

Stores validation outcomes.



Primary key:

validation\_result\_id



Foreign key:

rule\_id -> validation\_rule.rule\_id



This table is separated from business tables because validation results are audit information.



\### rejected\_record

Stores records rejected or sent to review.



Primary key:

rejected\_record\_id



Foreign key:

rule\_id -> validation\_rule.rule\_id



This table keeps rejected data traceable.



It stores:

\-source table

\-source record ID

\-source file

\-source row

\-rule ID

\-severity

\-rejection reason

\-raw payload

\-run ID



\### Primary Keys



Primary keys uniquely identify one row



sample.sample\_id

assay\_result.result\_id

shipment.shipment\_id

workflow\_event.event\_id

dim\_site.site\_code

dim\_analyte.analyte\_code

validation\_rule.rule\_id



Primary keys are important because every important record must be traceable



\### Foreign Keys

Foreign keys connect tables.



Main relationships:

sample.collection\_site\_code -> dim\_site.site\_code

assay\_result.sample\_id -> sample.sample\_id

assay\_result.analyte\_code -> dim\_analyte.analyte\_code

shipment.sample\_id -> sample.sample\_id

workflow\_event.sample\_id -> sample.sample\_id

validation\_result.rule\_id -> validation\_rule.rule\_id

rejected\_record.rule\_id -> validation\_rule.rule\_id



Foreign keys help protect data integrity

For example, an assay result should belong to an existing sample



\### Index Plan

Indexes are added to support common joins, filters, and quality checks



Indexes are useful on columns commonly used in:

JOIN

WHERE

GROUP BY

ORDER BY



Important indexes include:

\-sample.collection\_site\_code

\-sample.subject\_id

\-assay\_result.sample\_id

\-assay\_result.analyte\_code

\-assay\_result.sample\_id + analyte\_code + is\_current

\-shipment.sample\_id

\-shipment.status

\-workflow\_event.sample\_id

\-workflow\_event.event\_timestamp

\-validation\_result.rule\_id

\-validation\_result.source\_table + source\_record\_id

\-rejected\_record.rule\_id

\-rejected\_record.source\_table + source\_record\_id



Indexes should not be added randomly to every column

They help read performance, but too many indexes can slow down inserts and updates



\### Quality Checks

The file:

sql/quality\_checks.sql

contains SQL queries used to inspect data quality after records are loaded.



The checks include:

\-Orphan assay results

\-Duplicate current result versions

\-Detailed duplicate current result rows

\-Samples without workflow events

\-Current results outside reference range

\-Unit mismatches before reference-range comparison

\-Delayed shipments

\-Delivered shipments missing received\_at



Some checks should return zero rows

Example:

orphan assay results should return zero rows



Other checks may return rows for review

Example:

current results outside reference range may exist and should be reviewed



\### View Design

The schema includes:

sample\_quality\_summary\_view



A view is a saved query

It reads from normalized source tables and simplifies repeated joins



The view combines information from:

\-sample

\-dim\_site

\-assay\_result

\-shipment

\-workflow\_event



The view is useful for reporting and future feature exploration



\## View vs Denormalized Table

A view does not duplicate data.

It uses the normalized source tables when queried



This is useful because:

\-source tables remain the source of truth

\-logic is centralized

\-data is not copied unnecessarily



However, if the view becomes slow or too complex, it can later be converted into a denormalized physical table.



\## Denormalization Plan

Normalization is the default design choice, but it is not always the best final solution.



Denormalization may be useful when:

\-queries become too complicated

\-too many joins are required

\-reporting becomes slow

\-ML feature generation needs one ready-to-use table

\-the same joined dataset is used repeatedly



A future denormalized table could be:

sample\_quality\_summary

or:

sample\_feature\_table



This table could store precomputed values such as:

\-assay result count

\-shipment count

\-workflow event count

\-collection-to-received delay

\-shipment transit hours

\-retry/repeat message flag



The normalized tables would still remain the source of truth



\## Why Not Denormalize Immediately

The project starts with normalization because the relationships are still important and the schema should remain auditable



Denormalizing too early can create problems:

\-duplicated data

\-stale values

\-more refresh logic

\-harder debugging

\-unclear source of truth



For this reason, M5 uses a view first.

A physical denormalized table can be added later only if there is a clear performance or usability need

