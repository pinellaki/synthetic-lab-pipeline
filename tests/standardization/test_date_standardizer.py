from datetime import datetime

from src.standardization.date_standardizer import DateStandardizer


def test_standardize_iso_like_datetime() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize("2026-01-30 01:00")

    assert result == datetime(2026, 1, 30, 1, 0)


def test_standardize_day_first_datetime() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize("30/01/2026 01:00")

    assert result == datetime(2026, 1, 30, 1, 0)


def test_standardize_slash_datetime() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize("2026/01/30 01:00")

    assert result == datetime(2026, 1, 30, 1, 0)


def test_standardize_bad_datetime_returns_none() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize("bad date")

    assert result is None


def test_standardize_blank_datetime_returns_none() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize("")

    assert result is None


def test_standardize_none_datetime_returns_none() -> None:
    standardizer = DateStandardizer()

    result = standardizer.standardize(None)

    assert result is None