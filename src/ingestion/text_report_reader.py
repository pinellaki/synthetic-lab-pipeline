from pathlib import Path


class TextReportReader:
    def read_text(self, file_path: str) -> str:
        path = Path(file_path)

        with path.open(mode="r", encoding="utf-8") as text_file:
            return text_file.read()