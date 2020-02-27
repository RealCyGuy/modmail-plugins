import discord
from discord.ext import commands

import logging

logger = logging.getLogger("Modmail")

class RemoveSelfStars(commands.Cog):
    """Removes self-stars for starboard."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.Emoji == "⭐" and user == reaction.message.author:
            try:
                await reaction.remove(user)
            except discord.Forbidden:
                logger.error(f"I didn't have permissions to remove a self star from {user.name}#{user.discriminator}.")
            except Exception as e:
                logger.error(e)

def setup(bot):
    bot.add_cog(RemoveSelfStars(bot))
