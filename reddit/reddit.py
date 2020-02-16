import discord
from discord.ext import commands

import requests

from box import Box

from core.paginator import EmbedPaginatorSession

class RedditScroller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['memescroll'])
    async def memescroller(self, ctx, max=30):
        """
        Scroll through r/dankmemes.

        **Usage**:
        [p]memescroll 12 (returns 12 memes)
        [p]memescroll (returns 30 memes)
        [p]memescroll 3457345 (returns 100 memes)

        **Note**:
        The maximum amount of memes is 100.
        The default amount of memes is 30 (without specifying number).
        """
        subreddit = "dankmemes"
        r = requests.get(f"https://api.reddit.com/r/{subreddit}/top.json?sort=top&t=day&limit={max}",
                             headers={'User-agent': 'Super Bot 9000'})
        r = r.json()
        boxed = Box(r)

        embeds = []

        for post in boxed.data.children:
            data = post.data

            title = data.title
            image = data.url
            upvotes = data.ups
            subreddit = data.subreddit_name_prefixed

            embed = discord.Embed(title=title, color=0x9fdcf7)
            embed.set_image(url=image)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"On {subreddit} with {upvotes} upvotes.", value="\u200b", inline=False)

            embeds.append(embed)
            
        session = EmbedPaginatorSession(ctx, *embeds)
        await session.run()

def setup(bot):
    bot.add_cog(RedditScroller(bot))