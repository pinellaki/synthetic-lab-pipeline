M1 Project Structure
Summary

This document includes:

- Explanation of each project folder
- First 10 planned functions
- Logging, error, warning, and configuration plans


1. Project Tree


synthetic-lab-pipeline/

├── data/

│   ├── raw/

│   │   ├── api\_pages/

│   │   ├── pdf\_reports/

│   │   ├── text\_reports/

│   │   ├── assay\_results

│   │   ├── compound\_batches

│   │   ├── lab\_orders

│   │   ├── sample\_submissions

│   │   └── workflow\_events

│   ├── staging/

│   ├── trusted/

│   ├── rejected/

│   └── reports/

├── docs/

│   └── m1\_project\_structure.md

├── notebooks/

├── scripts/

├── sql/

├── src/

├── tests/

├── README.md

└── .gitignore

2. Explanation of Each Folder
data/

The data folder contains all project data files. It is divided into separate layers so raw, processed, rejected, and reporting data are not mixed together.

data/raw/

The raw folder contains the original exercise dataset files exactly as received. Files in this folder should not be manually changed.

data/staging/

The staging folder will contain intermediate cleaned or normalized data. Data in this folder may still need validation before it is trusted.

data/trusted/

The trusted folder will contain validated data that passed quality checks and is ready for analysis or reporting.

data/rejected/

The rejected folder will contain records or files that failed validation checks. These files should include enough information to understand why they were rejected.

data/reports/

The reports folder will contain generated output reports, summaries, metrics, and other final deliverables.

docs/

The docs folder contains project documentation, including design notes, structure explanations, milestone notes, and technical planning files.

notebooks/

The notebooks folder is reserved for exploratory analysis, experiments, and temporary investigation work.

scripts/

The scripts folder contains command-line scripts used to run pipeline steps manually or automatically.

sql/

The sql folder contains SQL scripts for database setup, queries, transformations, checks, and reporting logic.

src/

The src folder contains the main source code for the pipeline.

tests/

The tests folder contains automated tests for functions, validation rules, parsing logic, and pipeline behavior.

3. First 10 Functions

The first implementation should focus on small, testable functions. These functions should be created before building larger pipeline workflows.

1. load_config()

Loads project configuration values such as input paths, output paths, logging settings, and validation thresholds.

2. setup_logging()

Initializes project logging so pipeline execution can be monitored and debugged.

3. list_raw_files()

Scans the data/raw directory and returns the files available for processing.

4. read_csv_file()

Reads CSV files from the raw data folder and returns structured data for processing.

5. read_json_file()

Reads JSON files from the raw data folder and returns parsed JSON content.

6. read_text_file()

Reads text report files and returns their text content for downstream parsing.

7. validate_required_columns()

Checks whether a dataset contains all required columns before processing continues.

8. detect_missing_values()

Identifies missing or empty values in important fields.

9. write_staging_file()

Writes cleaned or partially processed data into the data/staging folder.

10. move_invalid_records()

Moves or writes invalid records into the data/rejected folder with a reason for rejection.

4. Logging Plan

The project should use structured logging to make the pipeline easier to debug and monitor.

The logging plan includes:

Log when the pipeline starts and finishes.
Log each file that is discovered in data/raw.
Log each file that is successfully processed.
Log validation failures.
Log rejected records and the reason for rejection.
Log unexpected errors with enough detail to investigate them.
Save logs to a file when the pipeline runs in production mode.
Print clear log messages to the console during local development.

Suggested logging levels:

INFO for normal pipeline progress.
WARNING for non-blocking issues.
ERROR for failures that stop one file or one processing step.
CRITICAL for failures that stop the whole pipeline.
5. Error Plan

Errors should be handled in a controlled way so that one bad file does not necessarily break the whole pipeline.

The error plan includes:

Use try and except blocks around file-reading operations.
Raise clear errors when required files are missing.
Raise clear errors when required columns are missing.
Send invalid records to data/rejected.
Keep processing other files when possible.
Stop the pipeline only when a critical dependency is missing.
Include the filename, function name, and reason in error messages.
Avoid hiding errors silently.

Examples of blocking errors:

Missing configuration file.
Missing data/raw folder.
Unsupported file format.
Required schema is unavailable.

Examples of non-blocking errors:

One invalid row in a CSV file.
One malformed text report.
One missing optional field.
6. Warning Plan

Warnings should be used when something is not ideal but the pipeline can continue.

The warning plan includes:

Warn when optional fields are missing.
Warn when a file is empty.
Warn when duplicate records are found.
Warn when unexpected columns are present.
Warn when a file has fewer records than expected.
Warn when a value is unusual but still valid.
Keep warnings visible in logs for later review.

Warnings should not stop the pipeline unless they exceed a defined threshold.

7. Configuration Plan

The project should avoid hardcoding important paths and settings directly inside functions.

Configuration should include:

Raw data path.
Staging data path.
Trusted data path.
Rejected data path.
Reports path.
Logging level.
Required column definitions.
Accepted file extensions.
Validation thresholds.
Runtime mode, such as development or production.

A future configuration file could be stored as:

config/config.yaml

or:

config/settings.json

For M1, basic configuration can start as constants inside the source code, but it should later move into a dedicated configuration file.




