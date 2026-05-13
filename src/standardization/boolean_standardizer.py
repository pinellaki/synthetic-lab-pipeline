from src.core.pipeline_constants import PipelineConstants


class BooleanStandardizer:
    def standardize(self, raw_value: str | None) -> bool | None:
        if raw_value is None:
            return None

        cleaned_value = raw_value.strip().lower()

        if cleaned_value == "":
            return None

        if cleaned_value in PipelineConstants.BOOLEAN_TRUE_VALUES:
            return True

        if cleaned_value in PipelineConstants.BOOLEAN_FALSE_VALUES:
            return False

        return None