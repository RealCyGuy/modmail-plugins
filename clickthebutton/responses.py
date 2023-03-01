import random

COOLDOWN_OVER = [
    "Button cooldown over!",
    "You can click the button now!",
    "The wait is over, it's time to take action!",
    "The moment has arrived, click away!",
    "It's time to unleash your powers on this button!",
    "The cooldown has ended, let the clicking begin!",
    "Your moment to shine has arrived, go ahead and click!",
    "The timer has expired, the button is waiting for you!",
    "The button has been given a new lease on life, take advantage of it!",
    "The clickfest can now continue, enjoy!",
    "The button has been revived and is awaiting your command.",
    "The button is now open for business, click to your heart's content!",
    "The button is eager for your click!",
    "The button is waiting patiently for your command.",
    "The button is refreshed and ready for action.",
    "The button has been anxiously awaiting your return.",
    "The button has been reborn and is now clickable again.",
    "The button has returned from its brief slumber.",
    "The button has been revitalized and is ready for your touch.",
    "The button is brimming with excitement to be clicked again.",
    "Get ready, the button is waiting for you!",
    "The cooldown has lifted, it's time to click!",
    "The button has been yearning for your click, now is the time!",
    "The button is eager to be clicked once more!",
    "The button is re-energized and ready for your click!",
    "The cooldown is over, it's time to click your heart out!",
    "The button is at your mercy once again!",
    "The button has been freed from its cooldown prison!",
    "It's time to resume the clicking madness, the cooldown is over!",
    "The button is back in action, waiting for your next move!",
]


def random_cooldown_over() -> str:
    return random.choice(COOLDOWN_OVER)


EMOJI_RANGES = [
    (0x1F600, 0x1F64F),  # Smiley & People
    (0x1F910, 0x1F93E),  # Emotion
    (0x1F950, 0x1F96C),  # Food & Drink
    (0x1F980, 0x1F9E0),  # Objects & Symbols
]


def random_emoji() -> str:
    emoji_range = random.choice(EMOJI_RANGES)
    return chr(random.randint(emoji_range[0], emoji_range[1]))


FOUGHT_OFF = [
    "fought off",
    "repelled",
    "defended against",
    "resisted",
    "battled against",
    "overcame",
    "beat back",
    "staved off",
    "held off",
    "thwarted",
    "warded off",
    "combated",
    "clashed with",
    "confronted",
    "countered",
    "withstood",
    "opposed",
    "fended off",
    "challenged",
    "contended with",
    "killed",  # requested by lyiam
]


def random_fought_off() -> str:
    return random.choice(FOUGHT_OFF)
