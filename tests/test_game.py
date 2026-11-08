
"""Tests for NoteToGo question generation."""

from random import Random

from app.core.game import QuestionGenerator
from app.core.levels import get_level
from app.core.models import Instrument


def create_generator(
    level_id: int = 1,
    instrument: Instrument = Instrument.PIANO,
    seed: int = 42,
) -> QuestionGenerator:
    """Create a predictable generator for testing."""

    return QuestionGenerator(
        level=get_level(level_id),
        selected_instrument=instrument,
        randomizer=Random(seed),
    )


def test_generate_question() -> None:
    generator = create_generator()

    question = generator.generate_question()

    assert question.question_id
    assert question.note.identifier.endswith("4")
    assert question.instrument == Instrument.PIANO


def test_beginner_questions_use_valid_notes() -> None:
    generator = create_generator(level_id=1)

    for _ in range(100):
        question = generator.generate_question()

        assert question.note.name in ("C", "D", "E")


def test_all_levels_respect_note_pools() -> None:
    for level_id in range(1, 6):
        generator = create_generator(level_id)

        for _ in range(100):
            question = generator.generate_question()

            assert (
                question.note.name
                in generator.level.note_names
            )


def test_consecutive_notes_are_different() -> None:
    generator = create_generator(level_id=1)

    previous_note = None

    for _ in range(100):
        question = generator.generate_question()

        assert question.note != previous_note

        previous_note = question.note


def test_questions_have_unique_ids() -> None:
    generator = create_generator()

    questions = [
        generator.generate_question()
        for _ in range(100)
    ]

    question_ids = {
        question.question_id for question in questions
    }

    assert len(question_ids) == 100


def test_selected_instrument_is_respected() -> None:
    generator = create_generator(
        level_id=3,
        instrument=Instrument.GUITAR,
    )

    for _ in range(50):
        question = generator.generate_question()

        assert question.instrument == Instrument.GUITAR


def test_master_level_supports_both_instruments() -> None:
    generator = create_generator(level_id=5)

    instruments = {
        generator.generate_question().instrument
        for _ in range(100)
    }

    assert instruments == {
        Instrument.PIANO,
        Instrument.GUITAR,
    }


def test_seeded_randomness_is_reproducible() -> None:
    first_generator = create_generator(seed=123)
    second_generator = create_generator(seed=123)

    first_sequence = [
        first_generator.generate_question().note.identifier
        for _ in range(20)
    ]

    second_sequence = [
        second_generator.generate_question().note.identifier
        for _ in range(20)
    ]

    assert first_sequence == second_sequence


def test_generators_have_independent_history() -> None:
    first_generator = create_generator(seed=10)
    second_generator = create_generator(seed=20)

    first_question = first_generator.generate_question()

    assert second_generator._previous_note is None

    second_question = second_generator.generate_question()

    assert first_generator._previous_note == first_question.note
    assert second_generator._previous_note == second_question.note
