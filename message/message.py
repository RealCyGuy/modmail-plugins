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

        self.decay_channels = dict()

        self.decay_loop.start()
        asyncio.create_task(self._set_val())


    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"},
            {
                "$set": {
                    "decay-channel": self.decay_channels,
                }
            },
            upsert=True,
        )

    async def _set_val(self):
        config = await self.db.find_one({"_id": "config"})

        if config is None:
            return

        self.decay_channels = config["decay-channel"]

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
        if str(ctx.channel.id) in self.decay_channels:
            self.decay_channels.pop(str(ctx.channel.id))
            msg = "Stopped decaying."
        else:
            self.decay_channels[str(ctx.channel.id)] = 86400000
            await ctx.send(self.decay_channels) #! Debugging
            msg = "Decaying!"

        await self._update_db()
        await ctx.send(msg)

    @tasks.loop(seconds=5.0)
    async def decay_loop(self):
        #! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        debug_user = self.bot.get_user(543225108135673877)
        await debug_user.send("I'm in the loop.")
        #! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        def is_deleteable(m):
            time_diff = m.created_at - datetime.datetime.now()
            return not m.pinned and time_diff < delta

        if self.decay_channels:
            for channel, time in self.decay_channels:
                delta = datetime.timedelta(milliseconds=time)
                d_channel = self.bot.get_channel(int(channel))

                await d_channel.send("in") #! Debugging

                deleted_messages = await d_channel.purge(check=is_deleteable)
                if deleted_messages > 0:
                    letter_s = "" if deleted_messages < 2 else "s"
                    confirm = await d_channel.send(
                        f"I deleted {deleted_messages} message{letter_s}!"
                    )
                    await asyncio.sleep(8)
                    await confirm.delete()
    
    @decay_loop.after_loop
    async def post_loop(self):
    if self.decay_loop.failed():
        import traceback
        error = self.your_task.exception()
        traceback.print_exception(type(error), error, error.__traceback__)



def setup(bot):
    bot.add_cog(MessageManager(bot))
