import discord
from discord.ext import commands

import logging
logger = logging.getLogger("Modmail")

import hashlib
import requests
import json
import os

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
                with open(os.path.join(os.path.dirname(__file__), "hashes.json"), "r") as f:
                    hashes = json.load(f)

                with open(os.path.join(os.path.dirname(__file__), "pokemon.jpg"), 'wb') as f:
                    f.write(image)

                with open(os.path.join(os.path.dirname(__file__), "pokemon.jpg"), "rb") as f:
                    md = hashlib.md5(f.read()).hexdigest()

                try:
                    pokemon = hashes[md]
                    await message.channel.send(f"My magical guessing powers guess it's a... {pokemon}.")
                except KeyError:
                    logger.info("Pokemon not found.")

def setup(bot):
    bot.add_cog(Pokecord(bot))