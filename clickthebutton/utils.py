import time


def event(text, content="") -> str:
    content = content.split("\n")
    content.append(f"<t:{int(time.time())}:f>: {text}")
    while len("\n".join(content)) > 2000:
        content.pop(0)
    return "\n".join(content)
