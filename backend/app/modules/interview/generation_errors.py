"""Controlled exhaustion; never a successful question or a grading decision."""


class QuestionGenerationUnavailable(Exception):
    """No valid, novel question exists within the bounded generation policy."""

    def __init__(
        self, topic: str, difficulty: str = "hard", reason: str = "fallback_exhausted"
    ):
        self.topic = topic
        self.difficulty = difficulty
        self.reason = reason
        super().__init__("A suitable question is temporarily unavailable.")

    @property
    def recovery_hint(self):
        if self.reason == "coverage_exhausted":
            return "No unused reviewed problem family remains for this session. You can end the interview without losing saved answers."
        return "No suitable question is available right now. Retry question generation to continue."
