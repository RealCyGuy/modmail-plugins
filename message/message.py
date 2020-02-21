import discord
from discord.ext import commands, tasks

import asyncio

from core import checks
from core.models import PermissionLevel
from core.paginator import EmbedPaginatorSession

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
            {"$set": {"decay-channel": self.decay_channels,}},
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

    @checks.has_permissions(PermissionLevel.ADMIN) # TODO: Set your own decay time.
    @commands.command()
    async def decay(self, ctx, channel: discord.TextChannel):
        """
        Deletes messages after some time in a channel except for pinned ones.

        Right now, the only time is 1 day.
        The only way to change it currently is through editing the database directly.
        """
        if str(channel.id) in self.decay_channels:
            self.decay_channels.pop(str(channel.id))
            msg = f"Stopped decaying in #{channel.name}."
        else:
            self.decay_channels[str(channel.id)] = 86400000
            msg = f"Decaying in #{channel.name}!"

        await self._update_db()
        await ctx.send(msg)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def decayinfo(self, ctx):
        if self.decay_channels:
            pages = []
            total = 0

            for channel in self.decay_channels:
                total += self.decay_channels[channel]
                
            average = total / len(self.decay_channels)

            front = discord.Embed(color=self.bot.main_color, title="All decay info.")
            front.add_field(
                name="Decay channels:",
                value=str(len(self.decay_channels)),
                inline=True,
            )
            front.add_field(
                name="Average decay time:",
                value=f"{str(average)}ms",
                inline=True,
            )
            front.add_field(
                name="To see channel specific info, use the reactions below.",
                value="\u200b",
                inline=False,
            )
            pages.append(front)

            for channel in self.decay_channels:
                d_channel = self.bot.get_channel(int(channel))
                page = discord.Embed(color=self.bot.main_color, title=f"Decay info of: #{d_channel.name}")
                page.add_field(name="Decay time:", value=f"{str(self.decay_channels[channel])}ms")

                pages.append(page)

            session = EmbedPaginatorSession(ctx, *pages)
            await session.run()    

        else:
            embed = discord.Embed(
                color=self.bot.error_color,
                title="No channels are decaying, to decay a channel use the command: `[p]decay #channel`",
            )
            await ctx.send(embed=embed)

    @tasks.loop(seconds=5.0)
    async def decay_loop(self):
        def is_deleteable(m):
            time_diff = datetime.datetime.now() - m.created_at
            return not m.pinned and time_diff > delta

        if self.decay_channels:
            for channel in self.decay_channels:
                delta = datetime.timedelta(milliseconds=self.decay_channels[channel])
                d_channel = self.bot.get_channel(int(channel))

                await d_channel.purge(check=is_deleteable)


def setup(bot):
    bot.add_cog(MessageManager(bot))
