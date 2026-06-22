"""Command-line entry point for loading source-document metadata."""

from src.database.postgres_source_document_loader import load_source_documents


def main() -> None:
    """Load source-document metadata into PostgreSQL."""
    loaded_count = load_source_documents()
    print(f"Source-document metadata rows loaded: {loaded_count}")


if __name__ == "__main__":
    main()