import discord
from discord.ext import commands

import requests

from box import Box

from core.models import EmbedPaginatorSession

class UrbanDictionary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def urban(self, ctx, *, search):
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
            for definition in data.list:
                page = discord.Embed()
                page.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)



def setup(bot):
    bot.add_cog(UrbanDictionary(bot))
