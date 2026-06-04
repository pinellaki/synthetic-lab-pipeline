START API INGESTION PIPELINE

1. Define the API contract
Define the API contract before writing the ingestion logic.

API endpoint:
    GET /api/v1/workflow-events

Purpose:
    Retrieve workflow status history for lab samples.

Authentication:
    Use an authentication header.
    The token must come from environment variables or a secret manager.
    Do not hardcode the token in Python code.

Authentication header:
    Authorization: Bearer <API_TOKEN>

Required parameters:
    page
    page_size

Optional parameters:
    updated_since
    sample_id
    status

Example request:
    GET /api/v1/workflow-events?page=1&page_size=100&updated_since=2026-01-01T00:00:00Z

Expected response shape:
    {
        "data": [
            {
                "event_id": "EVT-001",
                "sample_id": "SMP-001",
                "event_status": "received",
                "event_timestamp": "2026-05-20T10:05:00Z",
                "actor": "system",
                "message": "Sample received by lab"
            }
        ],
        "page": 1,
        "page_size": 100,
        "has_next_page": true,
        "next_page": 2
    }

Pagination signal:
    IF has_next_page is true:
        Continue with next_page.

    IF has_next_page is false:
        Stop pagination.

    IF next_page is null:
        Stop pagination.

Decision:
    The pipeline must not assume the first page is complete.
    It must continue until the API explicitly says there are no more pages.
    
2. Read configuration and credentials
Read API configuration before calling the API.

Get from environment/config:
    API base URL
    API token
    page size
    timeout seconds
    max retry count
    retry wait seconds

IF API base URL is missing:
    Stop the pipeline.
    Log configuration error.

IF API token is missing:
    Stop the pipeline.
    Log authentication configuration error.

Do not start API calls without valid configuration.

Credentials must come from:
    environment variables
    .env file ignored by Git
    secret manager

Credentials must NOT be:
    hardcoded in Python files
    committed to GitHub
    written inside README
    printed in logs
    
3. Start API ingestion run
Create a run_id for this ingestion execution.

Example:
    run_id = "API_WORKFLOW_EVENTS_2026_06_03_001"

Create a run log entry:
    run_id
    source = "workflow_events_api"
    started_at
    status = "running"

This run log describes the pipeline execution, not one sample status.

4. Initialize pagination
Set current_page = 1
Set page_size = configured page size
Set all_records = empty list
Set completed_pages = empty list

Decision:
    Use page_size from configuration.
    Do not hardcode it in the API call.

Reason:
    Different environments may need different page sizes.
    
5. Request one API page
WHILE there are more pages:

    Build request URL:
        endpoint = API_BASE_URL + "/api/v1/workflow-events"

    Build parameters:
        page = current_page
        page_size = configured page size
        updated_since = optional last successful load timestamp

    Build headers:
        Authorization = "Bearer " + API_TOKEN
        Accept = "application/json"

    Send GET request with timeout.

    Parameterization / safe construction:
        Do not concatenate raw user values directly into URLs.
        Use request parameters provided by the HTTP client.
        
 6. Handle API response status
 IF response status is 200:
    Continue processing the page.

ELSE IF response status is 401 or 403:
    Authentication or authorization failed.
    Do not retry.
    Mark run as failed.
    Log error without printing token.
    Stop pipeline.

ELSE IF response status is 400:
    Request is invalid.
    Do not retry until parameters are fixed.
    Mark run as failed.
    Log validation/configuration error.
    Stop pipeline.

ELSE IF response status is 429:
    Rate limit reached.
    Retry if retry limit has not been reached.
    Wait before retrying.

ELSE IF response status is 500, 502, 503, or 504:
    Server or temporary API problem.
    Retry if retry limit has not been reached.

ELSE:
    Unknown API error.
    Mark run as failed.
    Stop pipeline.
    
    
7. Retry policy
Retry only safe API read requests.

Safe to retry:
    GET requests for workflow events
    network timeout
    temporary server errors
    HTTP 429 rate limit
    HTTP 500 / 502 / 503 / 504

Not safe or not useful to retry:
    invalid token
    missing token
    forbidden access
    bad request caused by wrong parameters
    malformed endpoint
    schema mismatch that needs code fix

Retry policy:
    max_retries = 3
    wait time increases after each failure

Example:
    attempt 1: wait 2 seconds
    attempt 2: wait 5 seconds
    attempt 3: wait 10 seconds

IF all retry attempts fail:
    Mark the page as failed.
    Mark the run as failed.
    Do not pretend the API ingestion is complete.
    Stop the pipeline.
    
8. Validate page structure
After receiving a successful response:

    Parse JSON response.

    Check that response contains:
        data
        page
        page_size
        pagination signal

    IF data field is missing:
        Mark run as failed.
        Log response schema error.
        Stop pipeline.

    IF data is not a list:
        Mark run as failed.
        Log response schema error.
        Stop pipeline.

    IF pagination signal is missing:
        Mark run as failed.
        Reason:
            The pipeline cannot know whether the page is complete.
        Stop pipeline.
        
9. Complete-page condition
A page is complete only when:

    The API returns HTTP 200.
    The JSON body is valid.
    The data field exists.
    The data field is a list.
    All records in the page can be read.
    The pagination fields are present.
    The page number matches the requested page.
    The pipeline stores that page as completed.

IF all conditions are true:
    Add page number to completed_pages.
    Add records to all_records.

IF any condition fails:
    Do not mark the page complete.
    Mark the run as failed.
    Stop the load.
    
10. Failure behavior for missing pages
IF the API says next_page = 3
AND page 3 cannot be fetched:

    Retry page 3 according to retry policy.

    IF page 3 succeeds after retry:
        Continue normally.

    IF page 3 still fails:
        Mark run as failed.
        Do not continue to page 4.
        Do not save this API ingestion as complete.

Reason:
    If one page is missing, the dataset is incomplete.
    Continuing would create partial workflow history.

IF page sequence is broken:
    Example:
        page 1 completed
        page 2 missing
        page 3 available

    Decision:
        Stop at page 2 failure.
        Do not skip missing pages.
        
11. Convert API records into workflow_event records
FOR each record in all_records:

    Extract workflow event fields:
        event_id
        sample_id
        event_status
        event_timestamp
        actor
        message
        source_file or source_api
        source_page
        source_record_index
        ingested_at
        run_id

    Validate required fields:
        event_id is required
        sample_id is required
        event_timestamp is required
        event_status is required

    IF required fields are present:
        Create WorkflowEventRaw object.

    ELSE:
        Create rejected record.
        Store rejection reason.
        
12. workflow_event fields needed to track status history
workflow_event should contain:

    event_id:
        Unique identifier of the workflow event.

    sample_id:
        The sample affected by this event.

    event_status:
        The business status at that moment.
        Example: received, reviewed, approved, repeated, rejected.

    event_timestamp:
        When the status happened.

    actor:
        Who or what created the event.
        Example: system, analyst, API user, pipeline.

    message:
        Optional explanation or note.

    source_file / source_api:
        Where the event came from.

    source_page:
        API page number or file page.

    source_record_index:
        Position of the record inside the page.

    ingested_at:
        When the pipeline ingested the event.

    run_id:
        Which pipeline run ingested the event.
Why these fields matter:

They allow us to rebuild the full timeline of a sample.

Instead of only knowing the current status, we know:
    what happened
    when it happened
    who triggered it
    where the data came from
    which pipeline run loaded it
        
13. Store workflow events
FOR each valid workflow event:

    Insert into workflow_event table using parameterized SQL.

Required parameterization:
    event_id
    sample_id
    event_status
   