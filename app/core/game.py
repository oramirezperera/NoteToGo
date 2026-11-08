
"""Core question generation logic for NoteToGo."""

from dataclasses import dataclass, field
from random import Random
from uuid import uuid4

from app.core.levels import LevelConfig
from app.core.models import Instrument, Note


@dataclass(frozen=True)
class Question:
    """Represent a generated musical question."""

    question_id: str
    note: Note
    instrument: Instrument


@dataclass
class QuestionGenerator:
    """Generate random questions for one game session."""

    level: LevelConfig
    selected_instrument: Instrument
    randomizer: Random = field(
        default_factory=Random,
        repr=False,
    )

    _previous_note: Note | None = field(
        default=None,
        init=False,
        repr=False,
    )

    def generate_question(self) -> Question:
        """Generate a question using the level's rules."""

        available_notes = [
            Note(name)
            for name in self.level.note_names
        ]

        # Avoid immediately repeating the previous note.
        candidates = [
            note for note in available_notes
            if note != self._previous_note
        ]

        # A one-note level cannot avoid repetition.
        if not candidates:
            candidates = available_notes

        selected_note = self.randomizer.choice(candidates)

        if self.level.mixed_instruments:
            selected_instrument = self.randomizer.choice(
                list(Instrument)
            )
        else:
            selected_instrument = self.selected_instrument

        question = Question(
            question_id=str(uuid4()),
            note=selected_note,
            instrument=selected_instrument,
        )

        self._previous_note = selected_note

        return question
