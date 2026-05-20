M5 SQL check plan



The purpose of M5 is to use SQL to prove that the trusted database tables are connected correctly and do not contain obvious quality problems.



Check 1: Orphan results

Business question: Do all assay results belong to an existing sample?

Tables: assay\_result, sample

Logic: LEFT JOIN assay\_result to sample and return rows where sample is missing.

Expected result: zero rows.

Action if rows return: review or reject orphan results.



Check 2: Duplicate current versions

Business question: Does each sample/analyte have only one current result?

Tables: assay\_result

Logic: filter is\_current = true, group by sample\_id and analyte\_code, return groups with count greater than one.

Expected result: zero rows.

Action if rows return: block or review because there are conflicting current truths.



Check 3: Samples without workflow events

Business question: Does every sample have at least one workflow event?

Tables: sample, workflow\_event

Logic: LEFT JOIN sample to workflow\_event and return samples with no matching event.

Expected result: zero rows or explainable new samples.

Action if rows return: create warning/review and check workflow ingestion.



Check 4: Results outside reference range

Business question: Which current results are outside the analyte reference range?

Tables: assay\_result, dim\_analyte

Logic: join results to analyte reference and return current results where result\_value is below reference\_low or above reference\_high.

Expected result: rows may exist.

Action if rows return: warning/review, not automatic rejection, because real values can be outside reference range.



Check 5: Delayed shipments

Business question: Which shipments are marked delayed or took too long to arrive?

Tables: shipment

Logic: return shipments where status is delayed or transit time is above the business threshold.

Expected result: rows may exist.

Action if rows return: warning/review, and possibly use as early feature only if known before processing.

