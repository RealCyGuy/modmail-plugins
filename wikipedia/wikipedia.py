import discord
from discord.ext import commands
import wikipedia

class Wikipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wikipedia(self, ctx, *, search):
        """Searches on the english Wikipedia"""
        ctx.send(wikipedia.summary(search, sentences=1))

def setup(bot):
    bot.add_cog(Wikipedia(bot))