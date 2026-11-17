
"""Game session management for NoteToGo."""

from dataclasses import dataclass
from random import Random

from app.core.answers import AnswerResult, QuestionEvaluator
from app.core.game import Question, QuestionGenerator
from app.core.levels import LevelConfig
from app.core.models import Instrument


DEFAULT_SESSION_LENGTH = 10


@dataclass(frozen=True)
class SessionSummary:
    """Final statistics for a completed session."""

    total_questions: int
    correct_answers: int
    incorrect_answers: int
    accuracy_percentage: float


class GameSession:
    """Manage one complete NoteToGo game session."""

    def __init__(
        self,
        level: LevelConfig,
        selected_instrument: Instrument,
        question_count: int = DEFAULT_SESSION_LENGTH,
        randomizer: Random | None = None,
    ) -> None:
        if type(question_count) is not int or question_count < 1:
            raise ValueError(
                "Question count must be a positive integer."
            )

        self.level = level
        self.selected_instrument = selected_instrument
        self.question_count = question_count

        self._generator = QuestionGenerator(
            level=level,
            selected_instrument=selected_instrument,
            randomizer=(
                randomizer if randomizer is not None else Random()
            ),
        )

        self._started = False
        self._completed = False
        self._current_question: Question | None = None
        self._current_evaluator: QuestionEvaluator | None = None
        self._answers: list[AnswerResult] = []

    @property
    def is_started(self) -> bool:
        return self._started

    @property
    def is_completed(self) -> bool:
        return self._completed

    @property
    def current_question(self) -> Question | None:
        return self._current_question

    @property
    def answers(self) -> tuple[AnswerResult, ...]:
        """Expose a read-only snapshot of answer history."""
        return tuple(self._answers)

    @property
    def questions_answered(self) -> int:
        return len(self._answers)

    @property
    def current_question_number(self) -> int:
        """Return the current position in the session."""
        if not self._started:
            return 0

        return min(self.questions_answered + 1, self.question_count)

    def _create_question(self) -> Question:
        """Create and register the next active question."""

        question = self._generator.generate_question()

        evaluator = QuestionEvaluator(
            question=question,
            available_notes=self.level.note_names,
        )

        self._current_question = question
        self._current_evaluator = evaluator

        return question

    def start(self) -> Question:
        """Start a new session exactly once."""

        if self._started:
            raise RuntimeError(
                "This session has already started."
            )

        question = self._create_question()
        self._started = True

        return question

    def submit_answer(
        self,
        question_id: str,
        selected_note: str,
    ) -> AnswerResult:
        """Submit an answer for the active question."""

        if not self._started:
            raise RuntimeError("Session has not started.")

        if self._completed:
            raise RuntimeError("Session is already completed.")

        if self._current_evaluator is None:
            raise RuntimeError("No active question exists.")

        result = self._current_evaluator.submit_answer(
            question_id=question_id,
            selected_note=selected_note,
        )

        self._answers.append(result)

        if self.questions_answered == self.question_count:
            self._completed = True

        return result

    def next_question(self) -> Question:
        """Advance only after answering the current question."""

        if not self._started:
            raise RuntimeError("Session has not started.")

        if self._completed:
            raise RuntimeError("Session is already completed.")

        if (
            self._current_evaluator is None
            or not self._current_evaluator.is_answered
        ):
            raise RuntimeError(
                "Answer the current question before continuing."
            )

        return self._create_question()

    def get_summary(self) -> SessionSummary:
        """Return final statistics after session completion."""

        if not self._completed:
            raise RuntimeError(
                "Session must be completed before getting results."
            )

        correct_answers = sum(
            answer.is_correct for answer in self._answers
        )

        incorrect_answers = (
            self.questions_answered - correct_answers
        )

        accuracy = (
            correct_answers / self.questions_answered * 100
        )

        return SessionSummary(
            total_questions=self.questions_answered,
            correct_answers=correct_answers,
            incorrect_answers=incorrect_answers,
            accuracy_percentage=accuracy,
        )
