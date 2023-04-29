import random

import discord
from discord.ext import commands, tasks

from core import checks
from core.models import PermissionLevel


class RandomVCLimit(commands.Cog):
    """Automatically set a voice channel's member limit to a random value."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.channels = set()

    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {"channels": list(self.channels)}}, upsert=True
        )

    async def _get_db(self):
        config = await self.db.find_one({"_id": "config"})
        if config is None:
            return
        self.channels = set(config.get("channels", []))

    async def cog_load(self):
        await self._get_db()
        self.random_limit_loop.start()

    async def cog_unload(self):
        self.random_limit_loop.cancel()

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True)
    async def randomvc(self, ctx):
        """Get a list of random vcs."""
        await ctx.send(
            "Channels: "
            + ", ".join([f"`{c}` (<#{c.split('-')[1]}>)" for c in self.channels])
            + f"\nNext modification is <t:{int(self.random_limit_loop.next_iteration.timestamp())}:R>."
        )

    @checks.has_permissions(PermissionLevel.ADMIN)
    @randomvc.command()
    async def add(self, ctx, *, channel: discord.VoiceChannel):
        """Set the voice channel to be configured."""
        self.channels.add(str(ctx.guild.id) + "-" + str(channel.id))
        await self._update_db()
        await ctx.send(
            f"Added {channel.mention} to random vc list. It will be modified <t:{int(self.random_limit_loop.next_iteration.timestamp())}:R>."
        )

    @checks.has_permissions(PermissionLevel.ADMIN)
    @randomvc.command()
    async def remove(self, ctx, channel: str):
        """Remove a voice channel from the list."""
        try:
            self.channels.remove(channel)
        except KeyError:
            return await ctx.send("That channel is not in the list.")
        await self._update_db()
        await ctx.send(f"Removed {channel} from random vc list.")

    @tasks.loop(minutes=11)
    async def random_limit_loop(self):
        for channel in self.channels:
            guild_id, channel_id = channel.split("-")
            guild = self.bot.get_guild(int(guild_id))
            if guild is None:
                continue
            channel = guild.get_channel(int(channel_id))
            if channel is None:
                continue
            try:
                await channel.edit(user_limit=random.randint(2, 99))
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(RandomVCLimit(bot))
