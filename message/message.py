import discord
from discord.ext import commands

import asyncio

from core import checks
from core.models import PermissionLevel

class MessageManager(commands.Cog):
    """
    A plugin that... manages messages.
    
    It also has cool message-managing stuff.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @checks.has_permissions(PermissionLevel.MOD)
    @commands.command()
    async def clear(self, ctx, amount: int):
        """Clear messages."""
        if amount < 1:
            await ctx.send(
                embed=discord.Embed(
                    title=f"{amount} is too small! Please try again.", colour=self.bot.error_color
                )
            )
        else:
            deleted_messages = await ctx.channel.purge(limit=amount + 1)
            message_number = max(len(deleted_messages) - 1, 0)

            if message_number == 0:
                embed = discord.Embed(
                    title="No messages deleted.", colour=self.bot.error_color,
                )
            else:
                letter_s = "" if message_number < 2 else "s"
                embed = discord.Embed(
                    title=f"I have deleted {message_number} message{letter_s}!",
                    colour=self.bot.main_color,
                )

            confirm = await ctx.send(embed=embed)
            await asyncio.sleep(8)
            await confirm.delete()

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(aliases = ["aclear"],invoke_without_command=True)
    async def advancedclear(self, ctx):
        """
        Clearing messages, but advanced.
        """
        await ctx.send_help(ctx.command)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @advancedclear.command()
    async def contains(self, ctx, *, text):
        def is_in(m):
            return text.lower() in m.content

        deleted_messages = await ctx.channel.purge(check=is_in)
        message_number = max(len(deleted_messages) - 1, 0)

        if message_number == 0:
            embed = discord.Embed(
                title="No messages deleted.", colour=self.bot.error_color,
            )
        else:
            letter_s = "" if message_number < 2 else "s"
            embed = discord.Embed(
                title=f"I have deleted {message_number} message{letter_s}!",
                colour=self.bot.main_color,
            )

        confirm = await ctx.send(embed=embed)
        await asyncio.sleep(8)
        await confirm.delete()

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def decay(self, ctx, channel=None):
        if channel is None:
            channel = ctx.channel
        if type(channel) == discord.TextChannel:
            await ctx.send(channel)
        else:
            await ctx.send(embed=discord.Embed(colour=self.bot.error_color, title="Not a valid channel. :("))
        
        


def setup(bot):
    bot.add_cog(MessageManager(bot))
