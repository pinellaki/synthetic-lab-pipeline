from datetime import datetime


class DateStandardizer:
    DATE_FORMATS = [
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d %H:%M",
    ]

    def standardize(self, raw_datetime: str | None) -> datetime | None:
        if raw_datetime is None:
            return None

        cleaned_datetime = raw_datetime.strip()

        if cleaned_datetime == "":
            return None

        for date_format in self.DATE_FORMATS:
            parsed_datetime = self._try_parse(cleaned_datetime, date_format)

            if parsed_datetime is not None:
                return parsed_datetime

        return None

    def _try_parse(self, raw_datetime: str, date_format: str) -> datetime | None:
        try:
            return datetime.strptime(raw_datetime, date_format)
        except ValueError:
            return None