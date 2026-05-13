from src.features.leakage_checker import LeakageChecker


class FeatureTableBuilder:
    def __init__(self, leakage_checker: LeakageChecker) -> None:
        self.leakage_checker = leakage_checker

    def validate_feature_columns(self, feature_columns: list[str]) -> None:
        forbidden_columns = self.leakage_checker.find_forbidden_columns(
            feature_columns
        )

        if forbidden_columns:
            raise ValueError(
                f"Feature table contains leakage columns: {forbidden_columns}"
            )

    def build_empty_feature_row(self, sample_id: str) -> dict[str, str]:
        return {
            "sample_id": sample_id,
        }