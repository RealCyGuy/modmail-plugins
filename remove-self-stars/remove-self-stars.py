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
        if str(payload.emoji) != "\N{WHITE MEDIUM STAR}":
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        user = self.bot.get_user(payload.user_id)
        if user is None or user.bot:
            return

        if payload.user_id == message.author.id:
            try:
                await message.remove_reaction("\N{WHITE MEDIUM STAR}", user)
                logger.info(
                    f"I removed a self star from {user.name}#{user.discriminator}."
                )
            except discord.Forbidden:
                logger.error(
                    f"I didn't have permissions to remove a self star from {user.name}#{user.discriminator}."
                )


async def setup(bot):
    await bot.add_cog(RemoveSelfStars(bot))
