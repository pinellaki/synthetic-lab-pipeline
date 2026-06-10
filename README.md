# Synthetic Lab Pipeline

This repository contains the initial project structure for the Synthetic Lab Pipeline project.

## Project Structure

```text
synthetic-lab-pipeline/
├── README.md
├── .gitignore
│
├── src/
│   ├── **init**.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── **init**.py
│   │   ├── m8_schemas.py
│   │   └── m8_routes.py
│   │
│   ├── core/
│   │   ├── **init**.py
│   │   ├── app_config.py
│   │   ├── pipeline_constants.py
│   │   ├── pipeline_exception.py
│   │   └── logging_config.py
│   │
│   ├── schemas/
│   │   ├── **init**.py
│   │   ├── ingestion_metadata.py
│   │   ├── sample_submission_raw.py
│   │   ├── assay_result_raw.py
│   │   ├── shipment_raw.py
│   │   ├── workflow_event_raw.py
│   │   └── validation_result.py
│   │
│   ├── ingestion/
│   │   ├── **init**.py
│   │   ├── csv_reader.py
│   │   ├── excel_reader.py
│   │   ├── json_page_reader.py
│   │   ├── text_report_reader.py
│   │   ├── pdf_report_reader.py
│   │   └── ingestion_service.py
│   │
│   ├── pipeline/
│   │   ├── **init**.py
│   │   ├── sample_data_smoke_test.py
│   │   ├── sample_data_schema_test.py
│   │   ├── sample_data_standardization_test.py
│   │   ├── sample_data_validation_test.py
│   │   ├── sample_data_rejection_test.py
│   │   └── run_m8_sample_pipeline.py
│   │
│   ├── standardization/
│   │   ├── **init**.py
│   │   ├── sample_id_standardizer.py
│   │   ├── boolean_standardizer.py
│   │   ├── unit_standardizer.py
│   │   └── date_standardizer.py
│   │
│   ├── validation/
│   │   ├── **init**.py
│   │   ├── sample_submission_validator.py
│   │   ├── assay_result_validator.py
│   │   └── validation_service.py
│   │
│   ├── rejection/
│   │   ├── **init**.py
│   │   ├── rejected_record.py
│   │   ├── rejected_record_writer.py
│   │   └── rejection_service.py
│   │
│   ├── database/
│   │   ├── **init**.py
│   │   ├── database_config.py
│   │   └── database_service.py
│   │
│   └── features/
│       ├── **init**.py
│       ├── feature_table_builder.py
│       └── leakage_checker.py
│
├── tests/
│   ├── **init**.py
│   ├── standardization/
│   │   ├── **init**.py
│   │   ├── test_sample_id_standardizer.py
│   │   ├── test_boolean_standardizer.py
│   │   ├── test_unit_standardizer.py
│   │   └── test_date_standardizer.py
│   │
│   └── validation/
│       ├── **init**.py
│       ├── test_sample_submission_validator.py
│       └── test_assay_result_validator.py
│
├── data/
│   ├── raw/
│   │   ├── examples/
│   │   │   ├── sample_submissions.csv
│   │   │   ├── assay_results.csv
│   │   │   ├── shipments.csv
│   │   │   └── workflow_events.csv
│   │   ├── api_pages/
│   │   ├── pdf_reports/
│   │   └── text_reports/
│   │
│   ├── rejected/
│   │   └── .gitkeep
│   │
│   ├── reports/
│   ├── staging/
│   └── trusted/
│
├── sql/
│   ├── m5_database_schema.sql
│   └── quality_checks.sql
│
├── docs/
│   ├── m5_database_design.md
│   │
│   ├── diagrams/
│   │   └── database/
│   │       ├── M5_checks_database.png
│   │       └── M5_ERD_databse.png
│   │
│   ├── pseudocode/
│   │   ├── M5_database_pseudocode.md
│   │   ├── M6_Python_Transaction_Pseudocode.md
│   │   ├── M6_Transaction_Pseudocode.md
│   │   ├── M7_pseudocode.md
│   │   ├── M8_detailed_pseudocode.md
│   │   └── M8_simpler_pseudocode.md
│   │
│   └── sphinx/
│       ├── conf.py
│       ├── index.rst
│       ├── api.rst
│       ├── _static/
│       │   └── .gitkeep
│       └── _templates/
│           └── .gitkeep
│
└── requirements/
├── base.txt
├── dev.txt
└── prod.txt
```

## Folder Responsibilities

### `src/`

The `src/` folder contains the application code.

The code is organized in a FastAPI/Pydantic-style structure. Each folder has a clear responsibility, each file contains one main class, and each function should perform one specific operation.

### `src/core/`

Contains global project configuration and shared project-level utilities.

- `app_config.py` defines project configuration using Pydantic.
- `pipeline_constants.py` stores fixed values used across the pipeline.
- `pipeline_exception.py` defines the base custom pipeline exception.
- `logging_config.py` defines logging setup.

### `src/schemas/`

Contains Pydantic models used to represent data inside Python.

These schemas describe raw input records, ingestion metadata, and validation results.

Examples:

- `SampleSubmissionRaw` represents one raw row from `sample_submissions.csv`.
- `AssayResultRaw` represents one raw row from `assay_results.csv`.
- `IngestionMetadata` stores source traceability information.
- `ValidationResult` stores the result of one validation rule.

### `src/ingestion/`

Contains classes responsible for reading raw input files.

Each reader is responsible for one file type:

- `CsvReader` reads CSV files.
- `ExcelReader` reads Excel workbooks and sheets.
- `JsonPageReader` reads paginated JSON files.
- `TextReportReader` reads text reports.
- `PdfReportReader` extracts text from PDF reports.
- `IngestionService` coordinates the ingestion readers.

At this stage, ingestion preserves raw values and does not clean or validate data.

### `src/standardization/`

Contains classes responsible for converting raw values into standard formats.

Examples:

- `SampleIdStandardizer` standardizes sample IDs.
- `BooleanStandardizer` converts values like `yes`, `Y`, and `1` into booleans.
- `UnitStandardizer` maps unit variants to canonical units.
- `DateStandardizer` parses supported date formats.

Standardizers do not reject records. They only convert values when possible.

### `src/validation/`

Contains classes responsible for checking validation rules.

Examples:

- `SampleSubmissionValidator` validates sample intake rules.
- `AssayResultValidator` validates assay result rules.
- `ValidationService` coordinates validation checks.

Validators return a `ValidationResult` containing the rule result, severity, message, and action.

### `src/rejection/`

Contains classes responsible for rejected records.

- `RejectedRecord` represents one rejected record.
- `RejectedRecordWriter` writes rejected records to an output file.
- `RejectionService` coordinates rejected-record creation and writing.

Rejected records should be preserved for auditability and debugging.

### `src/database/`

Contains database-related configuration and service skeletons.

At this stage, the project does not yet connect to a real database. These files prepare the structure for later database integration.

### `src/features/`

Contains feature-engineering related skeletons.

- `LeakageChecker` checks that forbidden future-information columns are not used as ML features.
- `FeatureTableBuilder` prepares feature-table logic for later modules.

### `tests/`

The `tests/` folder contains unit tests.

Unit tests check small isolated functions and classes.

Current test areas:

- `tests/standardization/` checks standardizer classes.
- `tests/validation/` checks validator classes.

The tests currently use controlled example values, not the full raw dataset.

### `requirements/`

The `requirements/` folder stores Python dependencies.

- `base.txt` contains application dependencies.
- `dev.txt` contains development and testing dependencies.
- `prod.txt` contains production dependencies.

## Purpose

The goal of this project is to build a clean, testable, and auditable synthetic lab data pipeline.

The project is organized to separate the main responsibilities of the pipeline:

- raw file ingestion
- data representation with Pydantic schemas
- standardization of raw values
- validation of business rules
- rejected-record handling
- database preparation
- feature-engineering preparation
- unit testing

The current implementation focuses on project structure, M2 ingestion planning, and M3 standardization and validation logic.

The code follows the principle that each class should cover one kind of operation and each function should perform one specific task.

## Testing

The M3 standardization and validation logic is covered by unit tests.

To install development dependencies:

```powershell
python -m pip install -r requirements\dev.txt
```

To run the M3 tests:

```powershell
python -m pytest tests\standardization tests\validation
```

Current test result:

```text
44 passed
```

The tests prove that the standardization and validation functions work independently before connecting them to the full dataset pipeline.

## Notes

The real dataset should be stored under `data/raw/`.

The current M3 tests use small controlled example values inside the test files. They do not read the full raw dataset yet.

Generated Python cache folders such as `__pycache__/` should not be committed to GitHub.

## Branch

Initial setup work was done on the `week1-setup` branch.

Source-code organization work was done on the `organize-src-structure` branch.

M3 validation and standardization tests were added on the `m3-validation-tests` branch.