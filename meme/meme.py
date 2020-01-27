import discord
from discord.ext import commands
import requests
import random
from box import Box

class WildMemes(commands.Cog):
    """
    Randomly spawns memes.
    """
    subreddits = [
    "dankmemes",
    "wholesomememes",
    "memes",
    "terriblefacebookmemes",
    "historymemes",
    "me_irl",
    "2meirl4meirl",
    "fellowkids",
    "tumblr"
    ]

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        elif random.randint(0, 100) < 25:
            async with message.channel.typing():
                chosen_sub = random.choice(self.subreddits)
                r = requests.get(f"https://api.reddit.com/r/{chosen_sub}/top.json?sort=top&t=day&limit=500",
                             headers={'User-agent': 'Super Bot 9000'})
                r = r.json()
                boxed = Box(r)
                data = (random.choice(boxed.data.children)).data
                image = data.url
                upvotes = data.ups
                title = data.title
                subreddit = data.subreddit_name_prefixed
                embed = discord.Embed(title=f'Meme Title: {title}', color=0x6bdcd7)
                embed.set_author(name="A wild meme has appeared!")
                embed.set_image(url=image)
                embed.set_footer(text=f"On {subreddit} with {upvotes} upvotes.")
                await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(WildMemes(bot))