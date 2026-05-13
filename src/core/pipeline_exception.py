class PipelineException(Exception):
    def __init__(self, message: str, rule_id: str | None = None) -> None:
        self.message = message
        self.rule_id = rule_id
        super().__init__(self.message)