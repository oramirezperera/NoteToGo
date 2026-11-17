
"""Tests for NoteToGo answer validation."""

import pytest

from app.core.answers import QuestionEvaluator
from app.core.game import Question
from app.core.levels import get_level
from app.core.models import Instrument, Note


def create_evaluator() -> QuestionEvaluator:
    """Create an evaluator with a known correct answer."""

    question = Question(
        question_id="test-question-001",
        note=Note("C", 4),
        instrument=Instrument.PIANO,
    )

    return QuestionEvaluator(
        question=question,
        available_notes=get_level(1).note_names,
    )


def test_correct_answer() -> None:
    evaluator = create_evaluator()

    result = evaluator.submit_answer(
        question_id="test-question-001",
        selected_note="C",
    )

    assert result.is_correct is True
    assert result.selected_note == "C"
    assert result.correct_note == "C"
    assert evaluator.is_answered is True


def test_incorrect_answer() -> None:
    evaluator = create_evaluator()

    result = evaluator.submit_answer(
        question_id="test-question-001",
        selected_note="D",
    )

    assert result.is_correct is False
    assert result.selected_note == "D"
    assert result.correct_note == "C"


def test_question_starts_unanswered() -> None:
    evaluator = create_evaluator()

    assert evaluator.is_answered is False
    assert evaluator.result is None


def test_answer_result_is_stored() -> None:
    evaluator = create_evaluator()

    result = evaluator.submit_answer(
        "test-question-001", "C"
    )

    assert evaluator.result == result


def test_repeated_answer_is_rejected() -> None:
    evaluator = create_evaluator()

    evaluator.submit_answer("test-question-001", "C")

    with pytest.raises(RuntimeError):
        evaluator.submit_answer(
            "test-question-001", "C"
        )


def test_wrong_question_id_is_rejected() -> None:
    evaluator = create_evaluator()

    with pytest.raises(ValueError):
        evaluator.submit_answer(
            question_id="wrong-question",
            selected_note="C",
        )

    assert evaluator.is_answered is False


def test_invalid_answer_is_rejected() -> None:
    evaluator = create_evaluator()

    with pytest.raises(ValueError):
        evaluator.submit_answer(
            question_id="test-question-001",
            selected_note="H",
        )

    assert evaluator.is_answered is False


def test_note_outside_level_is_rejected() -> None:
    evaluator = create_evaluator()

    with pytest.raises(ValueError):
        evaluator.submit_answer(
            question_id="test-question-001",
            selected_note="G",
        )

    assert evaluator.is_answered is False


def test_invalid_answer_does_not_consume_question() -> None:
    evaluator = create_evaluator()

    with pytest.raises(ValueError):
        evaluator.submit_answer(
            "test-question-001", "H"
        )

    result = evaluator.submit_answer(
        "test-question-001", "C"
    )

    assert result.is_correct is True


def test_question_must_belong_to_answer_pool() -> None:
    question = Question(
        question_id="invalid-pool",
        note=Note("G"),
        instrument=Instrument.PIANO,
    )

    with pytest.raises(ValueError):
        QuestionEvaluator(
            question=question,
            available_notes=("C", "D", "E"),
        )
