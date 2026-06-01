"""Feature leakage checking utilities.

This module defines the LeakageChecker class.

The checker helps prevent data leakage by detecting columns that should not be
used as input features for future modelling or reporting logic.
"""


class LeakageChecker:
    """Detect forbidden feature columns that may cause data leakage.

    Data leakage happens when a feature contains information that would not be
    available at prediction time, or when the feature directly reveals the
    target outcome.

    This checker keeps a controlled set of forbidden columns and compares
    proposed feature columns against that set.
    """

    FORBIDDEN_FEATURE_COLUMNS = {
        "qc_status",
        "review_status",
        "approved_at",
        "result_value",
        "final_workflow_status",
    }

    def find_forbidden_columns(self, feature_columns: list[str]) -> list[str]:
        """Return forbidden columns found in a feature column list.

        Args:
            feature_columns: List of feature column names selected for a
                feature table.

        Returns:
            A list of column names that are present in both the input list and
            the forbidden leakage column set.

        Example:
            >>> checker = LeakageChecker()
            >>> checker.find_forbidden_columns(["sample_id", "qc_status"])
            ['qc_status']
        """
        return [
            column
            for column in feature_columns
            if column in self.FORBIDDEN_FEATURE_COLUMNS
        ]

    def has_leakage(self, feature_columns: list[str]) -> bool:
        """Return whether the feature column list contains leakage columns.

        Args:
            feature_columns: List of feature column names selected for a
                feature table.

        Returns:
            True if one or more forbidden leakage columns are found.
            False if no forbidden columns are found.
        """
        forbidden_columns = self.find_forbidden_columns(feature_columns)
        return len(forbidden_columns) > 0