import discord
from discord.ext import commands, tasks

import asyncio

from core import checks
from core.models import PermissionLevel

import datetime


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
                    title=f"{amount} is too small! Please try again.",
                    colour=self.bot.error_color,
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
    @commands.group(aliases=["aclear"], invoke_without_command=True)
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
    async def decay(self, ctx):
        config = await self.db.find_one({"id": "config"})
        if config["decay-channels"]["channels"] is None:
            channels = {}
            await ctx.send("It is none.")  #! ~Debugging~
        else:
            channels = config["decay-channels"]["channels"]

        await ctx.send(f"{channels} \n {type(channels)}")  #! ~Debugging~

        if str(ctx.channel.id) in channels:
            channels.pop(str(ctx.channel.id))
            msg = "Stopped decaying."
        else:
            channels[str(ctx.channel.id)] = 86400000
            msg = "Decaying!"

        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"decay-channels": {"channels": channels}}},
            upsert=True,
        )
        await ctx.send(msg)

    @tasks.loop(seconds=5)
    async def decay_loop(self):
        def is_deleteable(m):
            time_diff = m.created_at - datetime.datetime.now()
            return not m.pinned and time_diff < delta

        config = await self.db.find_one({"_id": "config"})
        channels = config["decay-channels"]["channels"]
        for channel, time in channels:
            delta = datetime.timedelta(milliseconds=time)
            d_channel = self.bot.get_channel(int(channel))

            deleted_messages = await d_channel.purge(check=is_deleteable)
            if deleted_messages > 0:
                letter_s = "" if deleted_messages < 2 else "s"
                confirm = await d_channel.send(
                    f"I deleted {deleted_messages} message{letter_s}!"
                )
                await asyncio.sleep(8)
                await confirm.delete()


def setup(bot):
    bot.add_cog(MessageManager(bot))
