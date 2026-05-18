from src.standardization.boolean_standardizer import BooleanStandardizer


def test_standardize_yes_returns_true() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("yes")

    assert result is True


def test_standardize_y_returns_true() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("Y")

    assert result is True


def test_standardize_one_returns_true() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("1")

    assert result is True


def test_standardize_no_returns_false() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("no")

    assert result is False


def test_standardize_n_returns_false() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("N")

    assert result is False


def test_standardize_zero_returns_false() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("0")

    assert result is False


def test_standardize_unknown_value_returns_none() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("maybe")

    assert result is None


def test_standardize_blank_value_returns_none() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize("")

    assert result is None


def test_standardize_none_returns_none() -> None:
    standardizer = BooleanStandardizer()

    result = standardizer.standardize(None)

    assert result is None