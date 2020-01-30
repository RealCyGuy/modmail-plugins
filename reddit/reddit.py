import discord
from discord.ext import commands

import requests

from box import Box

from core.paginator import EmbedPaginatorSession

class RedditScroller(commands.Cog):
    """See cursed images"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cursedimages(self, ctx):
        """Scroll through cursed images."""
        r = requests.get("https://api.reddit.com/r/cursedimages/top.json?sort=top&t=day&limit=10",
                     headers={'User Agent': 'Super Bot 9000'})
        r = r.json()
        r = Box(r)

        embeds = []

        for data in r.data.children.data:
            ctx.send(data)

def setup(bot):
    bot.add_cog(RedditScroller(bot))