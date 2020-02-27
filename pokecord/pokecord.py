import discord
from discord.ext import commands

import logging
logger = logging.getLogger("Modmail")

import hashlib
import requests

class Pokecord(commands.Cog):
    """
    Auto-guesses pokemon from pokecord.
    """
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 365975655608745985 and message.embeds:
            if message.embeds[0].title == "‌‌A wild pokémon has аppeаred!":
                image = requests.get(message.embeds[0].image.url).content
                with open("pokemon.jpg", 'wb') as f:
                    f.write(image)
    

def setup(bot):
    bot.add_cog(Pokecord(bot))