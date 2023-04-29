import os
from typing import TextIO


def open_data_file(name: str) -> TextIO:
    return open(
        os.path.join("..", "..", "clickthebutton", "data", name + ".txt"),
        "w",
        encoding="utf-8",
    )
