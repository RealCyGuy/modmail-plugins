import random
from datetime import timedelta

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
]


def random_cooldown_over() -> str:
    return random.choice(COOLDOWN_OVER)


EMOJIS = list(emoji.EMOJI_DATA.keys())


def random_emoji() -> str:
    return random.choice(EMOJIS)


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
    "gambled bo3 ct40 d100 with",
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
    "played the vienna gambit against",
    "played the queen's gambit declined exchange variation 4. d3 d6 5. Nf3 Nf6 6. e3 a6 7. a3 e5 8. d4 exd4 against",
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
    "congradulated",
    "shed a tear for",
    "teared apart",
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
]


def random_fought_off() -> str:
    verb = random.choice(FOUGHT_OFF)
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
]


def random_got_a_click() -> str:
    return random.choice(GOT_A_CLICK) + random_ending_punctuation()


def format_deltatime(delta: timedelta) -> str:
    seconds = delta.total_seconds()
    if seconds < 10:
        return f"{int(delta / timedelta(milliseconds=1))}ms"
    else:
        return f"{delta / timedelta(seconds=1):.3f}s"


COOKIES = [
    "{} used a click to buy a cookie.",
    "Bored with all their clicks, {} converted one a click into a cookie!",
    "Looks like {} has a sweet tooth! Enjoy your cookie.",
    "A cookie a day keeps the frowns away, right {}?",
    "{} just baked a fresh cookie!",
    "A cookie for you, {}!",
    "{} put hours of work into baking a cookie.",
    "Guess what, {}? You just got a cookie!",
    "{} took a cookie from a baby.",
]

EXCLAMATION = [
    "Yum",
    "Wow",
    "Yummy",
    "Delicious",
    "Tasty",
    "Scrumptious",
    "Mmm",
    "Divine",
]


def random_cookie(user: discord.User) -> str:
    return (
        random.choice(COOKIES).replace("{}", user.mention)
        + " "
        + random.choice(EXCLAMATION)
        + "!"
    )
