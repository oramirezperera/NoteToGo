
"""Difficulty configuration for NoteToGo."""

from dataclasses import dataclass

from app.core.models import NATURAL_NOTES


@dataclass(frozen=True)
class LevelConfig:
    """Define the rules of a difficulty level."""

    level_id: int
    name: str
    note_names: tuple[str, ...]
    minimum_questions: int
    mastery_accuracy: float
    minimum_per_note: int
    mixed_instruments: bool = False

    def __post_init__(self) -> None:
        """Validate the level configuration."""

        if self.level_id < 1:
            raise ValueError("Level ID must be positive.")

        if not self.note_names:
            raise ValueError("A level must contain notes.")

        if len(set(self.note_names)) != len(self.note_names):
            raise ValueError("Duplicate notes are not allowed.")

        if not all(
            note in NATURAL_NOTES for note in self.note_names
        ):
            raise ValueError("A level contains an invalid note.")

        if not 0 < self.mastery_accuracy <= 1:
            raise ValueError(
                "Mastery accuracy must be between 0 and 1."
            )

        if self.minimum_per_note < 1:
            raise ValueError(
                "Minimum exposure per note must be positive."
            )

        required_exposure = (
            len(self.note_names) * self.minimum_per_note
        )

        if self.minimum_questions < required_exposure:
            raise ValueError(
                "Minimum questions cannot be smaller than "
                "the required total note exposure."
            )


LEVEL_CONFIGS: tuple[LevelConfig, ...] = (
    LevelConfig(
        level_id=1,
        name="Beginner",
        note_names=("C", "D", "E"),
        minimum_questions=20,
        mastery_accuracy=0.80,
        minimum_per_note=3,
    ),
    LevelConfig(
        level_id=2,
        name="Explorer",
        note_names=("C", "D", "E", "F", "G"),
        minimum_questions=30,
        mastery_accuracy=0.80,
        minimum_per_note=3,
    ),
    LevelConfig(
        level_id=3,
        name="Apprentice",
        note_names=NATURAL_NOTES,
        minimum_questions=35,
        mastery_accuracy=0.85,
        minimum_per_note=3,
    ),
    LevelConfig(
        level_id=4,
        name="Musician",
        note_names=NATURAL_NOTES,
        minimum_questions=50,
        mastery_accuracy=0.90,
        minimum_per_note=5,
    ),
    LevelConfig(
        level_id=5,
        name="Ear Master",
        note_names=NATURAL_NOTES,
        minimum_questions=70,
        mastery_accuracy=0.90,
        minimum_per_note=5,
        mixed_instruments=True,
    ),
)


def get_level(level_id: int) -> LevelConfig:
    """Return the configuration for a given level."""

    for level in LEVEL_CONFIGS:
        if level.level_id == level_id:
            return level

    raise ValueError(f"Unknown difficulty level: {level_id}")
