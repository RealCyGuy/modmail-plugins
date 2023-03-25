import importlib
import inspect
import os
import glob
import pathlib
import sys
from unittest.mock import MagicMock

sys.path.append("../")

outputstart = []
outputend = ""

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
        lines = [line.strip() for line in lines]
        # if len(lines) > 1:
        #     doc = f"{lines[0]}<details><summary>More details</summary>{' '.join(lines[1:])}</details>"
        # doc = " ".join(doc.split())
        doc = "\n".join(lines)

    with open(os.path.join(folder, name + ".py"), "r", encoding="utf-8") as f:
        line = f.readline().strip("\n")
        if line.startswith("# registry: "):
            install = line[12:]
        else:
            install = f"realcyguy/modmail-plugins/{name}@v4"
    outputstart.append(f"[{name}](#{name})")
    outputend += (
        f"### {name}\n"
        f"```\n{doc}\n```\n"
        f'Source code: [`{name}.py`](https://github.com/RealCyGuy/modmail-plugins/blob/v4/{name}/{name}.py "{name} source code")  \n'
        f"Install: `?plugins install {install}`\n"
    )
output = " · ".join(outputstart) + "\n" + outputend
print(output)

try:
    import pyperclip
except ImportError:
    print("Couldn't copy to clipboard because pyperclip is not installed.")
else:
    pyperclip.copy(output)
    print("Copied to clipboard.")
