import time


def event(text, content="") -> str:
    content = content.split("\n")
    content.append(f"<t:{int(time.time())}:f>: {text}")
    while len("\n".join(content)) > 2000:
        content.pop(0)
    return "\n".join(content)


def find_data_intervals(values: list) -> list:
    intervals = []

    for value in values:
        intervals.append([value["clicks"][0] - 5, value["clicks"][-1] + 5])

    # combine overlapping intervals
    merged_intervals = []
    for interval in sorted(intervals):
        if not merged_intervals or (
            merged_intervals[-1][1] < interval[0]
            and interval[0] - merged_intervals[-1][1] >= 15
        ):
            merged_intervals.append(interval)
        else:
            merged_intervals[-1][1] = max(merged_intervals[-1][1], interval[1])

    return merged_intervals
