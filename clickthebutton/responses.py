import os

import random
from datetime import timedelta, datetime

import discord
import emoji

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
    "Click the button now.",
    "You may now click the button.",
    "The button fluttered its eyelashes at you - how you longed to click it!",
    "The button is now ready to be clicked.",
    "Breaking news: the button is now clickable again!",
    "Clickers of the world, rejoice! The button is now clickable again!",
    "The cooldown has cooled down, go click!",
    "Please click the button.",
    "The button is staring at you, waiting for you to click it.",
    '"Someone click me!" - the button',
    "HUZZAH! The button is now clickable again!",
    "Yippie! We can click the button again!",
    "Oh my, oh my God, you can click the button!",
    "Times up, click the button!",
    "Attention all clickers: the cooldown is over.",
    "Get your clicks up, not your funny up.",
    "Hello there, would you mind clicking the button?",
    "Did you know you can click the button now?",
    "The button is feeling a little shy, click it to make it feel better.",
    "If you click the button, you will be rewarded with a point!",
    "Can you be the first to click the button?",
    "Hurry up and click the button!",
    "Oh no. The button is back with a vengeance.",
    "Hurry! Click the button!",
    "Drop everything and click the button!",
    "If you don't click the button now, you will regret it.",
    "Woof! Woof! Click the button!",
    "After what felt like an eternity, the button is back!",
    "I know you're reading this. Click the button!",
    "Joke's over, click the button!",
    "The button wants your click.",
]


def random_cooldown_over() -> str:
    return random.choice(COOLDOWN_OVER)


EMOJIS = list(emoji.EMOJI_DATA.keys())


def random_emoji() -> str:
    return random.choice(EMOJIS)


def random_line(filename):
    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "data", filename),
        "r",
        encoding="utf-8",
    ) as f:
        while line := next(f):
            if line.startswith("# "):
                continue
            break
        for num, aline in enumerate(f, 2):
            if random.randrange(num):
                continue
            line = aline
    return line.strip()


MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


FOUGHT_OFF = [
    "fought off",
    "repelled",
    "defended against",
    "resisted",
    "battled against",
    "overcame",
    "beat back",
    "held off",
    "thwarted",
    "warded off",
    "combated",
    "combatted",
    "clashed with",
    "confronted",
    "countered",
    "withstood",
    "opposed",
    "fended off",
    "challenged",
    "contended with",
    "killed",  # requested by lyiam
    "foiled",
    "repulsed",
    "deterred",
    "hindered",
    "hindered the advance of",
    "quelled",
    "crushed",
    "subdued",
    "annihilated",
    "destroyed",
    "eliminated",
    "hugged",
    "licked",
    "slapped",
    "punched",
    "poked",
    "stabbed",
    "bit",
    "deflected",
    "blocked",
    "attacked",
    "flattened",
    "one-upped",
    "triumphed over",
    "ended",
    "absolutely humiliated",
    "licked",
    "shortyed",
    "pushed away",
    "tripped over",
    "deconstructed",
    "yelled at",
    "tripped",
    "high-fived",
    "played chess with",
    "didn't care about",
    "ignored",
    "went on a nice vacation to Hokkaido, Japan with",
    "purchased multiple pencils from",
    "dismissed",
    "intimidated",
    "compromised their details in a self-xss social engineering attack despite the advice of",
    "baked a Malay bahulu cake for",
    "poisoned",
    "added mercury to the water supply of",
    "burned",
    "started a war with",
    "dominated",
    "deleted",
    "stole the identity of",
    "reminisced about the good old days with",
    "started a cult with",
    "forged the signature of",
    "practiced their jump kicks on",
    "catfished",
    "won a game of russian roulette against",
    'performed a rendition of "I\'m a little teapot" for',
    "rejected",
    "refused to accept the lies of",
    "broke a promise to",
    "smiled at",
    "visited",
    "designed a new logo for",
    "avoided",
    "pretended to like",
    "assassinated",
    "hired a private investigator to follow",
    "dreamed about",
    "scammed",
    "snapped at",
    "presented the Academy Award for Best Picture to",
    "danced with",
    "didn't have to worry about",
    "used the force to push away",
    "called the police on",
    "cooked a meal for",
    "had a conversation with",
    "slandered",
    "learned about the true nature of",
    "choreographed a dance routine for",
    "played in a street band with",
    "smacked",
    ("gambled bo3 ct", lambda: random.randint(1, 100), " d100 with"),
    "made sure to think about the environment when dealing with",
    "followed the proper safety procedures while disposing of",
    "calculated the exact amount of time it would take to fall from the top of the Empire State Building while fighting",
    "made a slightly inappropriate joke about",
    "cornered",
    "snapped a photograph of",
    "decided to play checkers with",
    "sipped tea with",
    "attempted a backflip while fighting",
    "flicked",
    "pretended to steal the nose of",
    "violated the Geneva Convention by torturing",
    "froze the bank account of",
    "used the oldest trick in the book to defeat",
    "learned that the real clicks were the friends we made along the way with",
    "twirled their mustache while plotting against",
    "embezzled funds in order to pay for their lavish lifestyle while fighting",
    "went to medical school to learn how to treat the injuries they sustained while fighting",
    "was the only one who could stop",
    "stole the heart of",
    "won the Estonian parliamentary election against",
    "declined the queen's gambit against",
    "saw the error of their ways and decided to join forces with",
    "robbed",
    "outmaneuvered",
    "outsmarted",
    "outwitted",
    "outplayed",
    "outfoxed",
    "weatherd the storm of",
    "went head-to-head with",
    "went toe-to-toe with",
    "battled fiercely against",
    "locked horns with",
    "exchanged blows with",
    "exchanged guacamole recipes with",
    "broke the 4th wall with",
    "entered the void with",
    "manipulated",
    "backstabbed",
    "betrayed",
    "matched wits with",
    "didn't like the new Star Wars movie because of",
    "wasn't a fan of",
    "engaged in intellectual discourse with",
    "had a philosophical debate with",
    "worked alongside",
    "clicked faster than",
    "clicked the button with",
    "likes the dopamine rush they get from clicking the button more than",
    "started a cryptocurrency-based pyramid scheme with",
    "founded an artificial intelligence startup with",
    "interfered with",
    "squashed",
    "disrupted",
    "erased",
    "eradicated",
    "cleansed the world of",
    "destroyed the entire family tree of",
    "practiced tattooing foxes on the back of",
    "learned how to make a proper cup of tea from",
    "was a little bit disappointed with",
    "congratulated",
    "shed a tear for",
    "tore apart",
    "shredded",
    "ripped",
    "implanted a microchip in the brain of",
    "incepted a false memory in the mind of",
    "conducted a psychological experiment on",
    "led a highly successful raid on",
    "paralyzed",
    "survived a brawl with",
    "subscribed to",
    "stalked",
    "sent a friend request to",
    "unfortunately left the oven on while cooking a meal for",
    "beheaded",
    "outlived",
    "carefully seasoned",
    "stole {}'s cat",
    "stabbed {} with a polycarbonate spork",
    "drank {}'s blood",
    "robbed {} without consent",
    "challenged {} to a duel",
    "threw a rock at {}'s head",
    "collaborated with {} on a jazz album",
    "was overheard saying that {} is a bad person",
    "was frightened by {}'s appearance",
    "made {} cry about the social injustices of the world",
    "voiced suspicions about {} suspicious behaviour",
    "started an emergency meeting about",
    "was lost in {}'s eyes",
    "grabbed {} by the throat",
    "beat {} in a staring contest",
    "added too much salt to",
    "hypnotized",
    "winked at",
    "chewed carrots with",
    "deserved better than",
    "publicly embarrassed",
    "forgot to heal",
    "kneed",
    "kneeled before",
    "multiplied improper fractions with",
    ("practiced speaking ", lambda: random_line("languages.txt"), " with"),
    ("said an insult in ", lambda: random_line("languages.txt"), " to"),
    (
        'asked {} how to spell "',
        lambda: random_line("commonly_misspelled_words.txt"),
        '"',
    ),
    ('taught {} how to use the word "', lambda: random_line("words.txt"), '"'),
    ("used a ", lambda: random_line("colours.txt").lower(), " knife to cut"),
    ("watched ", lambda: random_line("2022_anime.txt"), " with"),
    ("went to ", lambda: random_line("countries.txt"), " with"),
    ("travelled to ", lambda: random_line("countries.txt"), " to escape"),
    ("dipped {} in ", lambda: random_line("dips.txt"), " before eating them"),
    ("thought ", lambda: MONTHS[datetime.now().month - 1], " was a good month to slap"),
    (
        "completed their ",
        lambda: datetime.now().year,
        " new year's resolution of getting revenge on",
    ),
    ("remembered what {} did in the ", lambda: random_line("armed_conflicts.txt")),
    (
        "listened to ",
        lambda: random_line("twice_songs.txt"),
        " by TWICE while fighting",
    ),
    ("performed a cover of ", lambda: random_line("twice_songs.txt"), " by TWICE with"),
    "ate {}'s homework",
    ("killed {} with their ", lambda: random_line("valorant_skins.txt")),
    ("ordered their ", lambda: random_line("cobras.txt"), " to bite"),
    (
        "thought that the K-pop artist ",
        lambda: random_line("kpop_artists.txt"),
        " was better than {}'s favourite, ",
        lambda: random_line("kpop_artists.txt"),
    ),
    (
        "distracted {} with an image of the K-pop artist ",
        lambda: random_line("kpop_artists.txt"),
    ),
    "three-starred",
    "literally doesn't care about",
    "convinced everyone that {} is the imposter",
    "thought {} was super sus",
    (
        "vented from ",
        lambda: random_line("skeld_locations.txt"),
        " to ",
        lambda: random_line("skeld_locations.txt"),
        " to kill",
    ),
    ("taught {} ", lambda: random_line("programming_languages.txt")),
    (
        "programmed in ",
        lambda: random_line("programming_languages.txt"),
        " despite the advice of",
    ),
    "gave a second chance to Cupid for",
    "cannibalized",
    (
        "outbid {} on the domain name ",
        lambda: random_line("words.txt").lower(),
        ".",
        lambda: random_line("tlds.txt").lower().encode().decode("idna"),
    ),
    'made {} say "Gosh darn it!"',
    (
        "defeaned {} by playing the ",
        lambda: random_line("instruments.txt").lower(),
        " so badly",
    ),
    "threw {}'s rank-up game",
    "lost their rank-up game to",
    "made {} so skeptical of love",
    "pushed down",
    "knocked over",
    ("used ", lambda: random_line("valorant_ultimates.txt"), " on"),
    ("outplayed {} with ", lambda: random_line("valorant_abilities.txt")),
    "stole {}'s ace",
    (
        "stream-sniped {} by landing at ",
        lambda: random_line("fortnite_named_locations.txt"),
    ),
    ("cranked 90s on {} in ", lambda: random_line("fortnite_named_locations.txt")),
    (
        "sent a message to {} containing their IP address, ",
        lambda: ".".join(str(random.randint(0, 255)) for _ in range(4)),
    ),
    ("played {} like a ", lambda: random_line("instruments.txt")),
    ("burned down {}'s ", lambda: random_line("agricultural_buildings.txt").lower()),
    (
        "flew from ",
        lambda: random_line("iata_codes.txt"),
        " airport to ",
        lambda: random_line("iata_codes.txt"),
        " with",
    ),
    "used the power of god and anime on",
    "deranked",
    ("played ", lambda: random_line("brawl_stars_brawlers.txt"), " against"),
    (
        "advised {} to try ",
        lambda: random_line("brawl_stars_brawlers.txt"),
        " in ",
        lambda: random_line("brawl_stars_maps.txt"),
    ),
    ("stabbed {} ", lambda: random.randint(1, 1000), " times"),
    (
        "taught {} that ",
        lambda: random_line("brawl_stars_brawlers.txt"),
        " is better than ",
        lambda: random_line("brawl_stars_brawlers.txt"),
    ),
    "played a trick on",
    "made quick work of",
    "made slow work of",
    "outranged",
    "out-dpsed",
    ("took advantage of {}'s ", lambda: random_line("phobias.txt")),
    ("helped develop {}'s ", lambda: random_line("phobias.txt")),
    ("gave {} ", lambda: random.randint(2, 59), " seconds of anxiety"),
    "figuratively killed",
    "ripped {} apart limb from limb, hypothetically speaking",
    "informed {} that their paternal parent is the CEO of Earth",
    "complained to {}'s manager",
    "was absolutely blown away by {}'s performance",
    "launched a nuclear missile at",
    "shot {} up, with their incredible generosity and thoughtfulness",
    "dropped a major truth bomb on",
    ("spoiled the next ", lambda: random.randint(2, 30), " years of {}'s life"),
]

SINGULAR_FOUGHT_OFF = [
    (
        "performed a ",
        lambda: random_line("instruments.txt"),
        " and ",
        lambda: random_line("instruments.txt"),
        " duet cover of ",
        lambda: random_line("twice_songs.txt"),
        " by TWICE with",
    ),
    ("played the ", lambda: random_line("chess_openings.txt"), " against"),
    "lost a 1v1 against",
    (
        "countered {}'s ",
        lambda: random_line("clash_royale_cards.txt").lower(),
        " with their ",
        lambda: random_line("clash_royale_cards.txt").lower(),
    ),
    (
        "destroyed {} with a ",
        lambda: random_line("clash_royale_cards.txt").lower(),
        " cycle deck",
    ),
    (
        "won a game of duo showdown with {} on ",
        lambda: random_line("brawl_stars_maps.txt"),
    ),
]


def random_fought_off(amount: int) -> str:
    if amount == 1:
        verb = random.choice(FOUGHT_OFF + SINGULAR_FOUGHT_OFF)
    else:
        verb = random.choice(FOUGHT_OFF)
    if type(verb) == tuple:
        verb = "".join([str(part()) if callable(part) else part for part in verb])
    if "{}" in verb:
        return verb
    if random.random() < 0.1:
        verb = verb.upper()
    if random.random() < 0.1:
        verb = "**" + verb + "**"
    if random.random() < 0.1:
        verb = "__" + verb + "__"
    if random.random() < 0.1:
        verb = "*" + verb + "*"
    return verb


ENDING_PUNCTUATION = [
    ".",
    "!",
    "!!",
    "!1!",
    "!?",
]


def random_ending_punctuation() -> str:
    return random.choices(ENDING_PUNCTUATION, cum_weights=(4, 5, 6, 7, 8))[0]


GOT_A_CLICK = [
    "got a click",
    "pressed the button",
    "secured a click",
    "smashed the button",
    "clicked successfully",
    "clicked the button",
    "obtained a click",
]


def random_got_a_click() -> str:
    return random.choice(GOT_A_CLICK) + random_ending_punctuation()


def format_deltatime(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    if seconds < 10:
        return f"{int(delta / timedelta(milliseconds=1))}ms"
    else:
        return f"{delta / timedelta(seconds=1):.3f}s"


DIVIDERS = [
    "-",
    "—",
    "―",
    "|",
    "/",
    "⇹",
    "★",
    "☆",
    "♥",
    "♡",
    "❣",
    "❉",
    "♪",
    "♫",
    "♬",
    "☮",
    "·",
    "~",
    "∼",
    "≀",
    "⋮",
    "⑅",
    "✳",
    "✯",
]


def random_divider() -> str:
    return random.choice(DIVIDERS)
