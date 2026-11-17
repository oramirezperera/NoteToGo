
"""Integration tests for the NoteToGo core game engine."""

from random import Random

import pytest

from app.core.levels import get_level
from app.core.models import Instrument
from app.core.session import GameSession


def create_session(
    level_id: int = 1,
    question_count: int = 10,
    seed: int = 42,
) -> GameSession:
    """Create a reproducible game session."""

    return GameSession(
        level=get_level(level_id),
        selected_instrument=Instrument.PIANO,
        question_count=question_count,
        randomizer=Random(seed),
    )


def play_session(
    session: GameSession,
    correct_answers: int,
) -> None:
    """Complete a session with a specified number of correct answers."""

    if not 0 <= correct_answers <= session.question_count:
        raise ValueError("Invalid correct-answer target.")

    question = session.start()

    for index in range(session.question_count):
        if index < correct_answers:
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

        if not session.is_completed:
            question = session.next_question()


@pytest.mark.parametrize("level_id", [1, 2, 3, 4, 5])
def test_full_session_at_every_level(level_id: int) -> None:
    """All five levels must support a complete game."""

    session = create_session(level_id=level_id)
    play_session(session, correct_answers=10)

    summary = session.get_summary()

    assert session.is_completed
    assert session.questions_answered == 10
    assert summary.total_questions == 10
    assert summary.correct_answers == 10
    assert summary.incorrect_answers == 0
    assert summary.accuracy_percentage == 100.0

    assert all(
        result.correct_note in session.level.note_names
        for result in session.answers
    )


def test_session_with_all_incorrect_answers() -> None:
    session = create_session()

    play_session(session, correct_answers=0)

    summary = session.get_summary()

    assert summary.correct_answers == 0
    assert summary.incorrect_answers == 10
    assert summary.accuracy_percentage == 0.0


def test_session_with_mixed_answers() -> None:
    session = create_session()

    play_session(session, correct_answers=7)

    summary = session.get_summary()

    assert summary.correct_answers == 7
    assert summary.incorrect_answers == 3
    assert summary.accuracy_percentage == 70.0


def test_invalid_answer_allows_recovery() -> None:
    session = create_session(question_count=1)
    question = session.start()

    with pytest.raises(ValueError):
        session.submit_answer(
            question.question_id,
            "H",
        )

    assert session.questions_answered == 0
    assert not session.is_completed

    result = session.submit_answer(
        question.question_id,
        question.note.name,
    )

    assert result.is_correct
    assert session.is_completed


def test_stale_and_duplicate_answers_are_rejected() -> None:
    session = create_session(question_count=2)
    first_question = session.start()

    session.submit_answer(
        first_question.question_id,
        first_question.note.name,
    )

    with pytest.raises(RuntimeError):
        session.submit_answer(
            first_question.question_id,
            first_question.note.name,
        )

    second_question = session.next_question()

    with pytest.raises(ValueError):
        session.submit_answer(
            first_question.question_id,
            first_question.note.name,
        )

    assert session.questions_answered == 1

    session.submit_answer(
        second_question.question_id,
        second_question.note.name,
    )

    assert session.is_completed
    assert session.questions_answered == 2


def test_independent_sessions() -> None:
    first = create_session(seed=10)
    second = create_session(seed=20)

    first_question = first.start()
    second_question = second.start()

    first.submit_answer(
        first_question.question_id,
        first_question.note.name,
    )

    assert first.questions_answered == 1
    assert second.questions_answered == 0

    second.submit_answer(
        second_question.question_id,
        second_question.note.name,
    )

    assert first.questions_answered == 1
    assert second.questions_answered == 1

    assert first_question.question_id != second_question.question_id
    assert first.answers != second.answers
