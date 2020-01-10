import discord
from discord.ext import commands
import wikipedia

class Wikipedia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wikipedia(self, ctx, *, search):
        """Searches on the english Wikipedia"""
        results = wikipedia.search(search)

        for result in results:
            try:
                page = wikipedia.page(result)
            except wikipedia.exceptions.DisambiguationError:
                ctx.send('DisambiguationError')
                continue
            except wikipedia.exceptions.PageError:
                ctx.send('PageError for result: ' + result)
                continue

            ctx.send(page.summary.encode('utf-8'))

def setup(bot):
    bot.add_cog(Wikipedia(bot))