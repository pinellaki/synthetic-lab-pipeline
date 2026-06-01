"""Feature table builder utilities.

This module defines the FeatureTableBuilder class.

The builder prepares feature-table structures and checks that selected feature
columns do not contain data leakage columns.
"""

from src.features.leakage_checker import LeakageChecker


class FeatureTableBuilder:
    """Build and validate feature-table structures.

    This class is responsible for feature-table preparation logic.

    At this stage, it performs two small operations:

    - validate that feature columns do not include leakage columns
    - create a minimal empty feature row for a sample

    More feature-engineering logic can be added later when the real dataset is
    connected to the pipeline.
    """

    def __init__(self, leakage_checker: LeakageChecker) -> None:
        """Initialize the feature table builder.

        Args:
            leakage_checker: Checker used to detect forbidden leakage columns.
        """
        self.leakage_checker = leakage_checker

    def validate_feature_columns(self, feature_columns: list[str]) -> None:
        """Validate that feature columns do not contain leakage columns.

        Args:
            feature_columns: List of feature column names selected for a
                feature table.

        Returns:
            None.

        Raises:
            ValueError: If one or more forbidden leakage columns are found.

        Notes:
            Data leakage happens when a feature contains information that would
            not be available at prediction time. This method prevents those
            columns from entering the feature table.
        """
        forbidden_columns = self.leakage_checker.find_forbidden_columns(
            feature_columns
        )

        if forbidden_columns:
            raise ValueError(
                f"Feature table contains leakage columns: {forbidden_columns}"
            )

    def build_empty_feature_row(self, sample_id: str) -> dict[str, str]:
        """Build a minimal empty feature row for one sample.

        Args:
            sample_id: Sample identifier for the feature row.

        Returns:
            A dictionary containing the sample identifier.

        Notes:
            This is a starting structure. More feature columns can be added
            later when feature engineering is implemented.
        """
        return {
            "sample_id": sample_id,
        }