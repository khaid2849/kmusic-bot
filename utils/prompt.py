import sys


class Prompt:
    def __init__(self, title: str, no_gui: bool = True):
        self.title = title
        self._no_gui = no_gui

    def prompt(self, message: str) -> str | None:
        if not sys.stdin.isatty():
            return None
        try:
            print(message, end="", flush=True)
            return input().strip()
        except (EOFError, KeyboardInterrupt):
            return None

    def alert(self, level: str, context: str, message: str) -> None:
        print(f"[{level.upper()}] [{context}] {message}", flush=True)

    @property
    def is_no_gui(self) -> bool:
        return self._no_gui
