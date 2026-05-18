from src.standardization.unit_standardizer import UnitStandardizer


def test_standardize_uppercase_mg_dl_returns_canonical_unit() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("MG/DL")

    assert result == "mg/dL"


def test_standardize_mg_per_dl_returns_canonical_unit() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("mg_per_dl")

    assert result == "mg/dL"


def test_standardize_u_l_returns_canonical_unit() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("u/l")

    assert result == "U/L"


def test_standardize_units_l_returns_canonical_unit() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("units/L")

    assert result == "U/L"


def test_standardize_mmol_per_l_returns_canonical_unit() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("mmol per L")

    assert result == "mmol/L"


def test_standardize_unknown_unit_returns_none() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("unknown_unit")

    assert result is None


def test_standardize_blank_unit_returns_none() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize("")

    assert result is None


def test_standardize_none_unit_returns_none() -> None:
    standardizer = UnitStandardizer()

    result = standardizer.standardize(None)

    assert result is None