
"""Tests for NoteToGo difficulty configurations."""

import pytest

from app.core.levels import LEVEL_CONFIGS, LevelConfig, get_level
from app.core.models import NATURAL_NOTES


def test_five_levels_exist() -> None:
    assert len(LEVEL_CONFIGS) == 5
    assert [level.level_id for level in LEVEL_CONFIGS] == [
        1, 2, 3, 4, 5
    ]


@pytest.mark.parametrize(
    ("level_id", "expected_notes"),
    [
        (1, ("C", "D", "E")),
        (2, ("C", "D", "E", "F", "G")),
        (3, NATURAL_NOTES),
        (4, NATURAL_NOTES),
        (5, NATURAL_NOTES),
    ],
)
def test_level_note_pools(
    level_id: int,
    expected_notes: tuple[str, ...],
) -> None:
    level = get_level(level_id)

    assert level.note_names == expected_notes


def test_level_one_mastery_requirements() -> None:
    level = get_level(1)

    assert level.minimum_questions == 20
    assert level.mastery_accuracy == 0.80
    assert level.minimum_per_note == 3


def test_level_five_uses_mixed_instruments() -> None:
    assert get_level(5).mixed_instruments is True


def test_earlier_levels_use_selected_instrument() -> None:
    for level in LEVEL_CONFIGS[:4]:
        assert level.mixed_instruments is False


def test_unknown_level_raises_error() -> None:
    with pytest.raises(ValueError):
        get_level(99)


def test_duplicate_notes_are_rejected() -> None:
    with pytest.raises(ValueError):
        LevelConfig(
            level_id=6,
            name="Invalid",
            note_names=("C", "C", "D"),
            minimum_questions=20,
            mastery_accuracy=0.80,
            minimum_per_note=3,
        )


def test_impossible_mastery_rules_are_rejected() -> None:
    with pytest.raises(ValueError):
        LevelConfig(
            level_id=6,
            name="Impossible",
            note_names=("C", "D", "E"),
            minimum_questions=10,
            mastery_accuracy=0.80,
            minimum_per_note=5,
        )


def test_invalid_accuracy_is_rejected() -> None:
    with pytest.raises(ValueError):
        LevelConfig(
            level_id=6,
            name="Invalid Accuracy",
            note_names=("C", "D", "E"),
            minimum_questions=20,
            mastery_accuracy=1.5,
            minimum_per_note=3,
        )


def test_level_config_is_immutable() -> None:
    level = get_level(1)

    with pytest.raises(AttributeError):
        level.name = "Changed"
