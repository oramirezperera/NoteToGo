
"""Answer validation for NoteToGo."""

from dataclasses import dataclass

from app.core.game import Question
from app.core.models import NATURAL_NOTES


@dataclass(frozen=True)
class AnswerResult:
    """Represent the result of one submitted answer."""

    question_id: str
    selected_note: str
    correct_note: str
    is_correct: bool


class QuestionEvaluator:
    """Evaluate one question and prevent repeated answers."""

    def __init__(
        self,
        question: Question,
        available_notes: tuple[str, ...],
    ) -> None:
        if not available_notes:
            raise ValueError("Available notes cannot be empty.")

        if any(
            note not in NATURAL_NOTES
            for note in available_notes
        ):
            raise ValueError("Available notes contain invalid values.")

        if len(set(available_notes)) != len(available_notes):
            raise ValueError("Duplicate available notes are not allowed.")

        if question.note.name not in available_notes:
            raise ValueError(
                "Question note must be an available answer."
            )

        self._question = question
        self._available_notes = available_notes
        self._result: AnswerResult | None = None

    @property
    def is_answered(self) -> bool:
        """Whether the question has already been answered."""
        return self._result is not None

    @property
    def result(self) -> AnswerResult | None:
        """Return the result, if an answer was submitted."""
        return self._result

    def submit_answer(
        self,
        question_id: str,
        selected_note: str,
    ) -> AnswerResult:
        """Validate and record a single answer."""

        if question_id != self._question.question_id:
            raise ValueError(
                "The submitted question ID does not match."
            )

        if self.is_answered:
            raise RuntimeError(
                "This question has already been answered."
            )

        if selected_note not in self._available_notes:
            raise ValueError(
                f"Invalid answer: {selected_note!r}."
            )

        is_correct = (
            selected_note == self._question.note.name
        )

        result = AnswerResult(
            question_id=self._question.question_id,
            selected_note=selected_note,
            correct_note=self._question.note.name,
            is_correct=is_correct,
        )

        self._result = result

        return result
