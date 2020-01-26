import discord
from discord.ext import commands

class ReactOnPing(commands.Cog):
    """Reacts with a ping emoji when someone gets pinged."""
    emojis = [
    "\N{REGIONAL INDICATOR LETTER P}",
    "\N{REGIONAL INDICATOR LETTER I}",
    "\N{REGIONAL INDICATOR LETTER N}",
    "\N{REGIONAL INDICATOR LETTER G}"
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if '<@' in message.content.upper():
            for emoji in self.emojis:
                await message.add_reaction(emoji)

def setup(bot):
    bot.add_cog(ReactOnPing(bot))