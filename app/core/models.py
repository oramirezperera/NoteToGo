
"""Core musical models for NoteToGo."""

from dataclasses import dataclass
from enum import Enum


NATURAL_NOTES: tuple[str, ...] = (
    "C", "D", "E", "F", "G", "A", "B"
)

DEFAULT_OCTAVE = 4


class Instrument(str, Enum):
    """Instruments supported by NoteToGo."""

    PIANO = "piano"
    GUITAR = "guitar"


@dataclass(frozen=True)
class Note:
    """Represent a musical note and its octave."""

    name: str
    octave: int = DEFAULT_OCTAVE

    def __post_init__(self) -> None:
        """Validate the note after initialization."""

        if self.name not in NATURAL_NOTES:
            raise ValueError(
                f"Invalid note: {self.name}. "
                f"Allowed notes: {NATURAL_NOTES}"
            )

        if type(self.octave) is not int or not 0 <= self.octave <= 8:
            raise ValueError(
                "Octave must be an integer between 0 and 8."
            )

    @property
    def identifier(self) -> str:
        """Return the note identifier, such as C4."""

        return f"{self.name}{self.octave}"
