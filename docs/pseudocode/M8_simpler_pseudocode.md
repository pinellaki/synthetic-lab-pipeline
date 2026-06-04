M8 API and workflow pseudocode plan



Start a new run and create run\_id.



Read shipment data from paginated JSON:

\- start with shipments\_page\_1.json

\- read page metadata: page, page\_size, next\_page

\- extract shipment records from data

\- add source\_file, source\_page, source\_record\_index, run\_id, ingested\_at

\- follow next\_page to the next file

\- continue until next\_page is null

\- log every page read

\- raise an error if a required next\_page is missing



Validate pagination:

\- check all expected pages were read

\- check last page has next\_page null

\- check no page was read twice

\- check total records read matches the pagination log



Standardize shipment records:

\- standardize sample\_id

\- parse shipped\_at, received\_at, api\_updated\_at

\- convert empty received\_at to null

\- parse condition\_temp\_c as numeric

\- standardize status values



Validate shipment records:

\- reject missing shipment\_id

\- reject missing sample\_id

\- warn/review duplicate shipment\_id

\- warn/review delivered shipments without received\_at

\- warn/review received\_at before shipped\_at

\- warn/review unknown status

\- warn/review orphan shipments whose sample\_id is not in sample



Read workflow\_events.csv:

\- read event\_id, sample\_id, event\_status, event\_timestamp, actor, message

\- add source\_file, source\_row, run\_id, ingested\_at

\- standardize sample\_id

\- parse event\_timestamp

\- validate required fields



Validate workflow:

\- check each event belongs to a known sample

\- check event order per sample

\- detect duplicate events

\- detect retry/repeat messages

\- create warnings for suspicious event order

\- create target signals from retry/repeat messages



Save outputs:

\- accepted shipment records

\- accepted workflow\_event records

\- shipment warnings/rejections

\- workflow warnings/rejections

\- API ingestion log

\- workflow status summary if needed



For ML:

\- shipment delay and temperature may be used as features only if available before processing

\- retry/repeat workflow messages can define the target, but should not be used as early features if they happen after intake

