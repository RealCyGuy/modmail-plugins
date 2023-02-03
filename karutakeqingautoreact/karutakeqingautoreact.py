import unicodedata
from typing import List

import discord
from discord.ext import commands


async def add_reactions(message: discord.Message, reactions: List[str]) -> None:
    for reaction in reactions:
        try:
            emoji = unicodedata.lookup(reaction)
        except KeyError:
            emoji = reaction
        try:
            await message.add_reaction(emoji)
        except discord.Forbidden:
            break


class KarutaKeqingAutoReact(commands.Cog):
    """
    Automatically add reactions to Karuta messages for Keqing Bot that usually requires premium.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == 646937666251915264 and message.embeds:
            embed = message.embeds[0]
            if embed.title.startswith("Card Collection"):
                await add_reactions(message, ["Left-Pointing Magnifying Glass", "Memo"])
            elif embed.title in ["Character Lookup", "Character Results"]:
                await add_reactions(message, ["🖌️", "Money Bag", "Revolving Hearts", "🎖️"])
            elif embed.title.startswith("Bits"):
                await add_reactions(message, ["Heavy Plus Sign"])


async def setup(bot):
    await bot.add_cog(KarutaKeqingAutoReact(bot))
