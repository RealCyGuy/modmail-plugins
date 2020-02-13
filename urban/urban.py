import discord
from discord.ext import commands

import requests

from box import Box

from core.paginator import EmbedPaginatorSession

class UrbanDictionary(commands.Cog):
    """
    Let's you search on the urban dictionary.
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def urban(self, ctx, *, search):
        """
        Search on the urban dictionary!
        """
        r = requests.get(f"https://api.urbandictionary.com/v0/define?term={search}",
                             headers={'User-agent': 'Super Bot 9000'})
        r = r.json()
        data = Box(r)

        if not data.list:
            embed = discord.Embed()
            embed.color = self.bot.error_color
            embed.title = "There is nothing here, try again."
            await ctx.send(embed=embed)
        else:
            pages = []
            for entry in data.list:
                definition = entry.definition.strip("[]")
                example = entry.example.strip("[]")


                page = discord.Embed(title=search)
                page.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                page.add_field(name=f"Definition: {definition}", value=f"Example: {example}")

                pages.append(page)
            session = EmbedPaginatorSession(ctx, *pages)
            await session.run()



def setup(bot):
    bot.add_cog(UrbanDictionary(bot))
