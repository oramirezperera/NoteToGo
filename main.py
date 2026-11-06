
"""Entry point for the NoteToGo web application."""

from nicegui import ui


@ui.page("/")
def home_page() -> None:
    """Render the initial NoteToGo welcome page."""

    with ui.column().classes(
        "w-full min-h-screen items-center justify-center "
        "gap-6 px-4"
    ):
        ui.icon("music_note", size="64px").classes("text-indigo-600")

        ui.label("NoteToGo").classes(
            "text-4xl font-bold text-center"
        )

        ui.label("Forge your musical instincts.").classes(
            "text-lg text-gray-600 text-center"
        )

        ui.label(
            "Train your ears. Recognize musical notes. "
            "Become a better musician."
        ).classes(
            "text-base text-center max-w-md"
        )

        ui.button(
            "Start Your Journey",
            on_click=lambda: ui.notify(
                "Welcome to NoteToGo!",
                type="positive",
            ),
        ).props("color=indigo size=lg")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="NoteToGo",
        favicon="🎵",
        host="127.0.0.1",
        port=8080,
        reload=True,
        show=False,
    )
