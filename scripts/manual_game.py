
"""Manual terminal test for the NoteToGo game engine."""

from app.core.levels import get_level
from app.core.models import Instrument
from app.core.session import GameSession


def play_game() -> None:
    """Run a small game session in the terminal."""

    session = GameSession(
        level=get_level(1),
        selected_instrument=Instrument.PIANO,
        question_count=3,
    )

    question = session.start()

    print("\nWelcome to NoteToGo!")
    print("Enter C, D, or E to answer.")
    print("Enter Q to quit.")

    while not session.is_completed:
        print(
            f"\nQuestion "
            f"{session.current_question_number}"
            f"/{session.question_count}"
        )

        # For development only.
        print(f"Debug note: {question.note.identifier}")

        while True:
            guess = input(
                "Your answer (C/D/E): "
            ).strip().upper()

            if guess == "Q":
                print("Game cancelled.")
                return

            if guess not in session.level.note_names:
                print(
                    "Invalid answer. "
                    "Please enter C, D, or E."
                )
                continue

            break

        result = session.submit_answer(
            question_id=question.question_id,
            selected_note=guess,
        )

        if result.is_correct:
            print("Correct!")
        else:
            print(
                f"Incorrect! "
                f"Correct answer: {result.correct_note}"
            )

        if not session.is_completed:
            question = session.next_question()

    summary = session.get_summary()

    print("\n--- SESSION RESULTS ---")
    print(f"Correct: {summary.correct_answers}")
    print(f"Incorrect: {summary.incorrect_answers}")
    print(
        f"Accuracy: "
        f"{summary.accuracy_percentage:.1f}%"
    )


if __name__ == "__main__":
    try:
        play_game()
    except (KeyboardInterrupt, EOFError):
        print("\nGame interrupted.")
