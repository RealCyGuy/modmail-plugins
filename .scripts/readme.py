import importlib
import inspect
import os
import glob
import pathlib
import sys
from unittest.mock import MagicMock

sys.path.append("../")

output = """| Name | Description | Install Command |
| --- | --- | --- |
"""

for folder in glob.iglob(os.path.join("../", "*", "")):
    name = pathlib.Path(folder).name
    while True:
        try:
            i = importlib.import_module(f"{name}.{name}")
        except ImportError as e:
            sys.modules[e.name] = MagicMock()
        else:
            break
    cog = None

    from discord.ext import commands

    for c in dir(i):
        item = getattr(i, c)
        if item and inspect.isclass(item) and isinstance(item, commands.CogMeta):
            cog = item

    if cog is None:
        continue

    doc = cog.__doc__
    if doc:
        doc = doc.strip()
        lines = doc.splitlines()
        if len(lines) > 1:
            doc = f"{lines[0]}<details><summary>More details</summary>{' '.join(lines[1:])}</details>"
        doc = " ".join(doc.split())

    output += (
        f"|"
        f"{name}<br>[`{name}.py`](https://github.com/RealCyGuy/modmail-plugins/blob/v4/{name}/{name}.py \"{name} source code\")  | "
        f"{doc} | "
        f"`?plugins install realcyguy/modmail-plugins/{name}@v4` |\n"
    )
print(output)

try:
    import pyperclip
except ImportError:
    print("Couldn't copy to clipboard because pyperclip is not installed.")
else:
    pyperclip.copy(output)
    print("Copied to clipboard.")
