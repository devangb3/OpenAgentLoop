from __future__ import annotations

import sys
from pathlib import Path


def read_text_input(path: Path | None) -> tuple[str, str]:
    if path is not None:
        return path.read_text(encoding="utf-8"), str(path)

    if sys.stdin.isatty():
        raise ValueError("No input provided. Pass --from/--diff or pipe text on stdin.")

    text = sys.stdin.read()
    if not text.strip():
        raise ValueError("Stdin was empty.")
    return text, "stdin"


def write_text_output(text: str, path: Path | None) -> None:
    if path is None:
        print(text)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text.rstrip()}\n", encoding="utf-8")
