
"""Tests for NoteToGo game sessions."""

from random import Random

import pytest

from app.core.levels import get_level
from app.core.models import Instrument
from app.core.session import GameSession


def create_session(
    question_count: int = 10,
) -> GameSession:
    """Create a predictable test session."""

    return GameSession(
        level=get_level(1),
        selected_instrument=Instrument.PIANO,
        question_count=question_count,
        randomizer=Random(42),
    )


def answer_current_question(
    session: GameSession,
    correctly: bool = True,
) -> None:
    """Answer the current question for testing."""

    question = session.current_question
    assert question is not None

    if correctly:
        selected_note = question.note.name
    else:
        selected_note = next(
            note for note in session.level.note_names
            if note != question.note.name
        )

    session.submit_answer(
        question_id=question.question_id,
        selected_note=selected_note,
    )


def test_session_starts_correctly() -> None:
    session = create_session()

    assert session.is_started is False

    question = session.start()

    assert session.is_started is True
    assert session.is_completed is False
    assert session.current_question == question
    assert session.current_question_number == 1


def test_session_cannot_start_twice() -> None:
    session = create_session()
    session.start()

    with pytest.raises(RuntimeError):
        session.start()


def test_cannot_answer_before_starting() -> None:
    session = create_session()

    with pytest.raises(RuntimeError):
        session.submit_answer("unknown", "C")


def test_cannot_skip_unanswered_question() -> None:
    session = create_session()
    session.start()

    with pytest.raises(RuntimeError):
        session.next_question()


def test_answer_increases_answer_count() -> None:
    session = create_session()
    session.start()

    answer_current_question(session)

    assert session.questions_answered == 1
    assert len(session.answers) == 1


def test_next_question_requires_previous_answer() -> None:
    session = create_session()
    first_question = session.start()

    answer_current_question(session)

    second_question = session.next_question()

    assert second_question.question_id != first_question.question_id
    assert second_question.note != first_question.note
    assert session.current_question_number == 2


def test_duplicate_answer_does_not_increase_count() -> None:
    session = create_session()
    question = session.start()

    answer_current_question(session)

    with pytest.raises(RuntimeError):
        session.submit_answer(
            question.question_id,
            question.note.name,
        )

    assert session.questions_answered == 1


def test_session_completes_after_final_answer() -> None:
    session = create_session(question_count=3)
    session.start()

    for index in range(3):
        answer_current_question(session)

        if index < 2:
            session.next_question()

    assert session.is_completed is True
    assert session.questions_answered == 3


def test_cannot_advance_after_completion() -> None:
    session = create_session(question_count=1)
    session.start()
    answer_current_question(session)

    with pytest.raises(RuntimeError):
        session.next_question()


def test_summary_requires_completed_session() -> None:
    session = create_session()
    session.start()

    with pytest.raises(RuntimeError):
        session.get_summary()


def test_session_summary_statistics() -> None:
    session = create_session(question_count=4)
    session.start()

    for index in range(4):
        answer_current_question(
            session,
            correctly=index < 3,
        )

        if index < 3:
            session.next_question()

    summary = session.get_summary()

    assert summary.total_questions == 4
    assert summary.correct_answers == 3
    assert summary.incorrect_answers == 1
    assert summary.accuracy_percentage == 75.0


def test_sessions_have_independent_state() -> None:
    first = create_session()
    second = create_session()

    first.start()
    second.start()

    answer_current_question(first)

    assert first.questions_answered == 1
    assert second.questions_answered == 0
    assert second.is_completed is False


def test_invalid_session_length() -> None:
    with pytest.raises(ValueError):
        create_session(question_count=0)
