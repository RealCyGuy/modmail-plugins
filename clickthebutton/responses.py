import asyncio
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List

import emoji

from .api import request_oeis
from .stats import Stats


def is_total_clicks_even(stats: Stats):
    return stats.total_clicks % 2 == 0


def players(stats: Stats):
    return stats.players


def total_clicks(stats: Stats):
    return stats.total_clicks


def streak_amount(stats: Stats) -> int:
    return stats.streak[1]


def streak_mention(stats: Stats) -> str:
    return "<@" + str(stats.streak[0]) + ">"


def random_mention(stats: Stats) -> str:
    return "<@" + str(random.choice(list(stats.leaderboard.keys()))) + ">"


def is_only_this_far_away(stats: Stats) -> str:
    amount = random.randint(2, 999)
    user_id, clicks = random.choice(list(stats.leaderboard.items()))
    return f"<@{user_id}> is only {amount} clicks away from reaching {clicks + amount}!"


def top_mention(stats: Stats) -> str:
    return "<@" + str(stats.sorted_leaderboard[0][0]) + ">"


def top_clicks(stats: Stats) -> int:
    return stats.sorted_leaderboard[0][1]


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
    "D'oh! Someone can click the button right now.",
    (
        "There are an ",
        lambda x: "even" if is_total_clicks_even(x) else "odd",
        " amount of clicks, someone should fix this!",
    ),
    ("Hello, ", random_mention, ", could you please click the above green button?"),
    is_only_this_far_away,
    (
        "If you want to be like the top clicker ",
        top_mention,
        ", you should start clicking NOW!",
    ),
    (
        "For most people, ",
        top_clicks,
        " clicks seem unreachable, but you should never give up.",
    ),
    (
        '"Wow, ',
        top_mention,
        " is so cool with ",
        top_clicks,
        ' clicks! I should click right now." - you, probably.',
    ),
    (
        "Do you suffer from ",
        lambda x: random_line("phobias.txt"),
        "? Click the button!",
    ),
    (
        lambda x: MONTHS[datetime.now().month - 1],
        " is the best month to click the button!",
    ),
    (
        "Hey ",
        lambda x: random_emoji(),
        " everyone ",
        lambda x: random_emoji(),
        " ",
        lambda x: random_emoji(),
        " Would ",
        lambda x: random_emoji(),
        " you ",
        lambda x: random_emoji(),
        " be ",
        lambda x: random_emoji(),
        " so ",
        lambda x: random_emoji(),
        " kind ",
        lambda x: random_emoji(),
        " to click ",
        lambda x: random_emoji() * random.randint(1, 2),
        " the button? ",
        lambda x: random_emoji() * random.randint(1, 2),
        " Thank you!",
    ),
    "Click marathon, round two! The button's ready for some finger gymnastics.",
    "The button's back from its coffee break. Click it like you mean it!",
    "Button's recharged and feeling clicky. Give it some love!",
    "The cooldown's over! Unleash your clicker fury.",
    "Click alert! The button is thirsting for your touch.",
    "Button's back online. Time for a clicking fiesta!",
    "The button's had its rest. Now, pester it with clicks!",
    "Ready, set, click! The button's missed your touch.",
    "Button's up and awake! Poke it with clicks.",
    "The button's cooldown is history. Time for a clicking spree!",
    "Button's vacation is over. Time to get back to clicking!",
    "The button's nap time has ended. Wake it up with your clicks!",
    "Clickety-click! The button is ready for round two!",
    "The button's timeout is up. Click frenzy begins now.",
    "Rested and ready! The button awaits your clicking prowess.",
    "Button's ready for some action. Let the clicking commence!",
    "Cooldown's done. The button is hungry for clicks.",
]


def random_cooldown_over(stats: Stats) -> str:
    selections = COOLDOWN_OVER.copy()
    if stats.players > 1:
        selections.extend(
            [
                (
                    "Only ",
                    players,
                    " people have clicked the button. Can someone new click it?",
                ),
                (
                    "There are already ",
                    players,
                    " happy button clickers! Please join in!",
                ),
            ]
        )
    if stats.streak:
        selections.extend(
            [
                (
                    "Someone click before ",
                    streak_mention,
                    " can continue their streak!",
                ),
                (
                    streak_mention,
                    ", you are one click away from reaching a streak of ",
                    lambda x: streak_amount(x) + 1,
                ),
            ]
        )
    selected = random.choice(selections)
    if callable(selected):
        selected = selected(stats)
    elif type(selected) == tuple:
        selected = "".join(
            [str(part(stats)) if callable(part) else part for part in selected]
        )
    return selected


EMOJIS = [
    key
    for key, value in emoji.EMOJI_DATA.items()
    if value["status"] == emoji.STATUS["fully_qualified"]
]


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


def random_line_with_a_or_an(filename):
    line = random_line(filename)
    return (
        ("an" if any(line.lower().startswith(vowel) for vowel in "aeiou") else "a")
        + " "
        + line
    )


def random_censored_words(style: str = r"\*", count: int = 1, random_word=True) -> str:
    words = []
    for x in range(count):
        words.append(style * random.randint(*random.choice([(3, 6), (4, 8)])))
    if random_word:
        words.append(random_line("words.txt"))
        random.shuffle(words)
    return " " + " ".join(words)


async def random_oeis_sequence() -> str:
    try:
        sequence, oeis_id = await request_oeis()
    except:
        sequence = (
            "0, 1, 1, 1, 2, 1, 2, 1, 5, 2, 2, 1, 5, 1, 2, 1, 14, 1, 5, 1, 5, 2, 2, 1, 15, 2, 2, 5, 4, 1, 4, 1, "
            "51, 1, 2, 1, 14, 1, 2, 2, 14, 1, 6, 1, 4, 2, 2, 1, 52, 2, 5, 1, 5, 1, 15, 2, 13, 2, 2, 1, 13, 1, "
            "2, 4, 267, 1, 4, 1, 5, 1, 4, 1, 50, 1, 2, 3, 4, 1, 6, 1, 52, 15, 2, 1, 15, 1, 2, 1, 12, 1, 10, "
            "1, 4, 2"
        )
        oeis_id = "A000001"
    return f"[{sequence}](<https://oeis.org/{oeis_id}>)"


def random_anime() -> str:
    anilist_id, title = random_line("anime.txt").split(maxsplit=1)
    return f"[{title}](<https://anilist.co/anime/{anilist_id}>)"


def random_anime_tags() -> str:
    anilist_id, tags = random_line("anime_tags.txt").split(maxsplit=1)
    tags = tags.split(",")
    random.shuffle(tags)
    tags = tags[: random.randint(4, 10)]
    return f"[{', '.join(tags)}](<https://anilist.co/anime/{anilist_id}>)"


def random_rps_win() -> str:
    choices = ["rock", "paper", "scissors"]
    choice = random.randint(0, 2)
    one = choices[choice]
    if choice == 0:
        two = choices[2]
    else:
        two = choices[choice - 1]
    return f"{one} against {{}}'s {two}"


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
    ("used ", lambda: random_line_with_a_or_an("colours.txt").lower(), " knife to cut"),
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
    "ripped {} apart limb from limb, hypothetically speaking,",
    "informed {} that their paternal parent is the CEO of Earth",
    "complained to {}'s manager",
    "was absolutely blown away by {}'s performance",
    "launched a nuclear missile at",
    "shot {} up, with their incredible generosity and thoughtfulness,",
    "dropped a major truth bomb on",
    ("spoiled the next ", lambda: random.randint(2, 30), " years of {}'s life"),
    "did not let {}'s actions slide",
    ", a woodchuck, answered {}'s burning question concerning the amount of wood a woodchuck could chuck if a woodchuck could chuck wood",
    "made {}'s jaw drop",
    "sold seashells by the seashore to",
    "went neck and neck with",
    ("slapped {} with ", lambda: random_line_with_a_or_an("fish.txt").lower()),
    'did not say "bless you" when {} sneezed',
    (
        "used ",
        lambda: random_line("pokemon_moves.txt"),
        " on {} (it's ",
        lambda: random.choice(["super effective!", "not very effective"]),
        ")",
    ),
    ('told {} "', lambda: random_line("proverbs.txt"), '"'),
    ("flexed their ", lambda: random_line("valorant_skins.txt"), " on"),
    "dueled",
    "gave {} a slap on the wrist",
    "made {} tremble",
    "predicted all of {}'s moves",
    "forgot about",
    (
        "solved {}'s problem in ",
        lambda: random_line("time_complexities.txt").lower(),
        " time",
    ),
    "soloed",
    "one-tapped",
    "full boxed",
    "hit a clip on",
    "ate",
    "baked a cake with",
    "borrowed {}'s favorite book",
    "danced tango with",
    "shared secrets under the stars with",
    "got lost in a maze with",
    "won a chess game against",
    "painted a portrait of",
    "had a picnic in the park with",
    "traded hats with",
    "built a sandcastle with",
    "went on a road trip with",
    "cooked a gourmet meal for",
    "watched a meteor shower with",
    "planted a garden with",
    "wrote a poem about",
    "had better vision than",
    "beat [Sliding Game](<https://realcyguy.itch.io/sliding-game>) faster than {}, achieving the [world record](<https://www.speedrun.com/sliding>),",
    "sent {} into a deep hole",
    "differentiated",
    (lambda: random_censored_words(count=random.randint(1, 3)),),
    (lambda: random_censored_words(style="#", count=random.randint(1, 3)),),
    ("compared {} to ", random_oeis_sequence),
    (lambda: random_censored_words(count=random.randint(4, 9)),),
    ("confused {} with the numbers ", random_oeis_sequence),
    ("watched ", random_anime, " with"),
    ("introduced {} to ", random_anime),
    ("knew {} was interested in ", random_anime_tags),
    ("diverted {} with an anime about ", random_anime_tags),
    (
        "provided {} with [a relevant XKCD](<https://xkcd.com/",
        lambda: random.randint(1, 2889),
        ">)",
    ),
]

SINGULAR_FOUGHT_OFF = [
    (
        "performed ",
        lambda: random_line_with_a_or_an("instruments.txt"),
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
        lambda: random_line("brawl_stars_duos_maps.txt"),
    ),
    "won a 1v1 against",
    ("enjoyed a {}-free ", lambda: MONTHS[datetime.now().month - 1]),
    "sang a duet at karaoke with {}",
    ("played ", random_rps_win),
]


async def random_fought_off(amount: int) -> str:
    if amount == 1:
        verb = random.choice(FOUGHT_OFF + SINGULAR_FOUGHT_OFF)
    else:
        verb = random.choice(FOUGHT_OFF)
    if type(verb) is tuple:
        parts = []
        for part in verb:
            if callable(part):
                part = part()
                if asyncio.iscoroutine(part):
                    part = await part
                parts.append(str(part))
            else:
                parts.append(part)
        verb = "".join(parts)
    if not verb[0].isalpha():
        return verb
    if "{}" in verb:
        return " " + verb
    if random.random() < 0.1:
        verb = verb.upper()
    if random.random() < 0.1:
        verb = "**" + verb + "**"
    if random.random() < 0.1:
        verb = "__" + verb + "__"
    if random.random() < 0.1:
        verb = "*" + verb + "*"
    return " " + verb


ENDING_PUNCTUATION = [
    ".",
    "!",
    "!!",
    "!1!",
    "!?",
    "~",
    "...",
    "!!!",
]


def random_ending_punctuation() -> str:
    return random.choices(ENDING_PUNCTUATION, cum_weights=(4, 5, 6, 7, 8, 9, 10, 11))[0]


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
    "𝄞",
]


def random_divider() -> str:
    return random.choice(DIVIDERS) + "\ufe0e"


def format_mentions(
    clicker_ids: List[int], clickers_dict: Dict[int, datetime], edited_at: datetime
) -> str:
    formatted = list(
        f"<@{user_id}> ({format_deltatime(clickers_dict[user_id] - edited_at)})"
        for user_id in clicker_ids
    )
    if len(formatted) <= 2:
        return " and ".join(formatted)
    else:
        return ", ".join(formatted[:-1]) + ", and " + formatted[-1]
