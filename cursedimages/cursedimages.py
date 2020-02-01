import discord
from discord.ext import commands

import requests

from box import Box

from core.paginator import EmbedPaginatorSession

class CursedImages(commands.Cog):
    """See cursed images."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cursedimages(self, ctx):
        """Scroll through cursed images."""
        subreddit = "cursedimages"
        r = requests.get(f"https://api.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit=10",
                             headers={'User-agent': 'Super Bot 9000'})
        r = r.json()
        boxed = Box(r)

        embeds = []

        for post in boxed.data.children:
            data = post.data

            title = data.title
            image = data.url
            upvotes = data.ups

            embed = discord.Embed(title=title, color=0x22ddbbff)
            embed.set_image(url=image)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(value=f"{upvotes} upvotes.", inline=False)

            embeds.append(embed)
            
        session = EmbedPaginatorSession(ctx, *embeds)
        await session.run()

def setup(bot):
    bot.add_cog(CursedImages(bot))