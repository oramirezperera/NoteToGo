
"""Tests for NoteToGo musical models."""

import pytest

from app.core.models import Instrument, Note


def test_create_valid_note() -> None:
    note = Note(name="C", octave=4)

    assert note.name == "C"
    assert note.octave == 4
    assert note.identifier == "C4"


def test_default_octave() -> None:
    note = Note(name="A")

    assert note.identifier == "A4"


def test_invalid_note_raises_error() -> None:
    with pytest.raises(ValueError):
        Note(name="H", octave=4)


def test_invalid_octave_raises_error() -> None:
    with pytest.raises(ValueError):
        Note(name="C", octave=9)


def test_note_is_immutable() -> None:
    note = Note(name="C", octave=4)

    with pytest.raises(AttributeError):
        note.name = "D"


def test_supported_instruments() -> None:
    assert Instrument.PIANO.value == "piano"
    assert Instrument.GUITAR.value == "guitar"


def test_note_equality() -> None:
    first_note = Note("C", 4)
    second_note = Note("C", 4)

    assert first_note == second_note
