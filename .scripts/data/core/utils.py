import os
from typing import TextIO


def open_data_file(name: str) -> TextIO:
    return open(
        os.path.join("..", "..", "clickthebutton", "data", name + ".txt"),
        "w",
        encoding="utf-8",
    )


def contains_swear(text: str) -> bool:
    return any(word in text for word in ["fuck", "bitch", "dick", "sex"])
