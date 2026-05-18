from src.standardization.sample_id_standardizer import SampleIdStandardizer


def test_standardize_lowercase_sample_id() -> None:
    standardizer = SampleIdStandardizer()

    result = standardizer.standardize("smp-2026-00042")

    assert result == "SMP-2026-00042"


def test_standardize_sample_id_with_spaces() -> None:
    standardizer = SampleIdStandardizer()

    result = standardizer.standardize(" SMP-2026-00042 ")

    assert result == "SMP-2026-00042"


def test_standardize_blank_sample_id_returns_none() -> None:
    standardizer = SampleIdStandardizer()

    result = standardizer.standardize("")

    assert result is None


def test_standardize_none_sample_id_returns_none() -> None:
    standardizer = SampleIdStandardizer()

    result = standardizer.standardize(None)

    assert result is None