class SampleIdStandardizer:
    def standardize(self, sample_id: str | None) -> str | None:
        if sample_id is None:
            return None

        cleaned_sample_id = sample_id.strip().upper()

        if cleaned_sample_id == "":
            return None

        return cleaned_sample_id