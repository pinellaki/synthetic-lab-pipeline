class LeakageChecker:
    FORBIDDEN_FEATURE_COLUMNS = {
        "qc_status",
        "review_status",
        "approved_at",
        "result_value",
        "final_workflow_status",
    }

    def find_forbidden_columns(self, feature_columns: list[str]) -> list[str]:
        return [
            column
            for column in feature_columns
            if column in self.FORBIDDEN_FEATURE_COLUMNS
        ]

    def has_leakage(self, feature_columns: list[str]) -> bool:
        forbidden_columns = self.find_forbidden_columns(feature_columns)
        return len(forbidden_columns) > 0