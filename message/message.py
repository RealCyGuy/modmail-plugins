import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class MessageManager(commands.Cog):
    """
    A plugin that... manages messages.
    
    It also has cool message stuff.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    @checks.has_permissions(PermissionLevel.MOD)
    async def clear(self, ctx, amount: int):
        """Clear messages"""
        if number < 1:
            await ctx.send(
                embed=discord.Embed(
                    title="Too small! Please try again.", colour=self.bot.error_color
                )
            )
        else:
            deleted_messages = await ctx.channel.purge(limit=amount + 1)
            message_number = max(len(deleted_messages) - 1, 0)

            if message_number == 0:
                embed = discord.Embed(
                    title="No messages deleted.",
                    colour=self.bot.error_color,
                )
            else:
                embed = discord.Embed(
                    title=f"I have deleted {message_number} message{" " if message_number < 2 else " s "}!",
                    colour=self.bot.main_color,
                )

            confirm = await ctx.send(embed=embed)
            await asyncio.sleep(8)
            await confirm.delete()
    
    @checks.has_permissions(PermissionLevel.MOD)
    @commands.group(invoke_without_command=True)
    async def advancedclear(self, ctx):
        """
        Clearing messages, but advanced.
        """
        await ctx.send(embed=embed)

    @advancedclear.command()


def setup(bot):
    bot.add_cog(MessageManager(bot))
