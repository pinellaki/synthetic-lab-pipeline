from pathlib import Path


class PdfReportReader:
    def extract_text(self, file_path: str) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as error:
            raise ImportError(
                "pypdf is required to extract text from PDF reports."
            ) from error

        path = Path(file_path)
        reader = PdfReader(str(path))

        page_texts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_texts.append(page_text)

        return "\n".join(page_texts)