import discord
from discord.ext import commands

import asyncio

from core import checks
from core.models import PermissionLevel

def clear_messages(self, ctx, amount, check=None):
    deleted_messages = await ctx.channel.purge(limit=amount + 1, check=check)
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

class MessageManager(commands.Cog):
    """
    A plugin that... manages messages.
    
    It also has cool message-managing stuff.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MOD)
    async def clear(self, ctx, amount: int):
        """Clear messages."""
        clear_messages(self, ctx, amount)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True)
    async def advancedclear(self, ctx):
        """
        Clearing messages, but advanced.
        """
        await ctx.send_help(ctx.command)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @advancedclear.command()
    async def link(self, ctx, link):
        pass
        


def setup(bot):
    bot.add_cog(MessageManager(bot))
