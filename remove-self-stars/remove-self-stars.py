import discord
from discord.ext import commands

import logging

logger = logging.getLogger("Modmail")


class RemoveSelfStars(commands.Cog):
    """Removes self-stars for starboard."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        try:
            message = await payload.member.fetch_message(payload.message_id)
            if payload.emoji == "⭐" and payload.user_id == message.author.id:
                try:
                    await message.remove_reaction(payload.member, "⭐")
                except discord.Forbidden:
                    logger.error(
                        f"I didn't have permissions to remove a self star from {payload.member.name}#{pauload.member.discriminator}."
                    )
                except Exception as e:
                    logger.error(e)
        except discord.NotFound:  # Not a self-star.
            pass


def setup(bot):
    bot.add_cog(RemoveSelfStars(bot))
