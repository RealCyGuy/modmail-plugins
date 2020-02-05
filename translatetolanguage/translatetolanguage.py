# originally from piyush: https://github.com/officialpiyush/modmail-plugins/translator
import discord
from discord.ext import commands

from googletrans import Translator


class TranslateToLanguage(commands.Cog):
    """I translate text."""
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    self.languagelist = {
        "afrikaans": "af",
        "albanian": "sq",
        "amharic": "am",
        "arabic": "ar",
        "armenian": "hy",
        "azerbaijani": "az",
        "basque": "eu",
        "belarusian": "be",
        "bengali": "bn",
        "bosnian": "bs",
        "bulgarian": "bg",
        "catalan": "ca",
        "cebuano": "ceb",
        "chichewa": "ny",
        "chinese-simplified": "zh-cn",
        "chinese-traditional": "zh-tw",
        "corsican": "co",
        "croatian": "hr",
        "czech": "cs",
        "danish": "da",
        "dutch": "nl",
        "english": "en",
        "esperanto": "eo",
        "estonian": "et",
        "filipino": "tl",
        "finnish": "fi",
        "french": "fr",
        "frisian": "fy",
        "galician": "gl",
        "georgian": "ka",
        "german": "de",
        "greek": "el",
        "gujarati": "gu",
        "haitian-creole": "ht",
        "hausa": "ha",
        "hawaiian": "haw",
        "hebrew": "iw",
        "hindi": "hi",
        "hmong": "hmn",
        "hungarian": "hu",
        "icelandic": "is",
        "igbo": "ig",
        "indonesian": "id",
        "irish": "ga",
        "italian": "it",
        "japanese": "ja",
        "javanese": "jw",
        "kannada": "kn",
        "kazakh": "kk",
        "khmer": "km",
        "korean": "ko",
        "kurdish-kurmanji": "ku",
        "kyrgyz": "ky",
        "lao": "lo",
        "latin": "la",
        "latvian": "lv",
        "lithuanian": "lt",
        "luxembourgish": "lb",
        "macedonian": "mk",
        "malagasy": "mg",
        "malay": "ms",
        "malayalam": "ml",
        "maltese": "mt",
        "maori": "mi",
        "marathi": "mr",
        "mongolian": "mn",
        "myanmar-burmese": "my",
        "nepali": "ne",
        "norwegian": "no",
        "pashto": "ps",
        "persian": "fa",
        "polish": "pl",
        "portuguese": "pt",
        "punjabi": "pa",
        "romanian": "ro",
        "russian": "ru",
        "samoan": "sm",
        "scots-gaelic": "gd",
        "serbian": "sr",
        "sesotho": "st",
        "shona": "sn",
        "sindhi": "sd",
        "sinhala": "si",
        "slovak": "sk",
        "slovenian": "sl",
        "somali": "so",
        "spanish": "es",
        "sundanese": "su",
        "swahili": "sw",
        "swedish": "sv",
        "tajik": "tg",
        "tamil": "ta",
        "telugu": "te",
        "thai": "th",
        "turkish": "tr",
        "ukrainian": "uk",
        "urdu": "ur",
        "uzbek": "uz",
        "vietnamese": "vi",
        "welsh": "cy",
        "xhosa": "xh",
        "yiddish": "yi",
        "yoruba": "yo",
        "zulu": "zu",
        "Filipino": "fil",
        "Hebrew": "he",
    }

    @commands.command(aliases=["ttl"])
    async def translatetextlanguage(self, ctx, language, *, message):
        """Translates a provided message into the specified language."""
        try:
            tmsg = self.translator.translate(message, dest=language)
            embed = discord.Embed()
            embed.color = 4388013
            embed.description = tmsg.text
        except ValueError:
            embed = discord.Embed
            embed.color = self.bot.error_color
            embed.title = 'Invalid language. Use [p]languages for the usable languages.'
        ctx.send(embed=embed)

    @commands.command()
    async def languages(self, ctx):
        """List of languages."""
        desc = ""
        for lang in self.languagelist:
            desc += f"`{lang}`: `{self.languagelist[lang]}`"

        embed = discord.Embed()
        embed.title = "Use the code on the right for the translate command."
        embed.color = 0x1ED4E0FF
        embed.description = desc
        ctx.send(embed=Embed)

def setup(bot):
    bot.add_cog(TranslateToLanguage(bot))
