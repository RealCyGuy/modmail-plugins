import asyncio
import datetime

import discord
from discord.ext import commands

from bot import ModmailBot
from core import checks
from core.models import PermissionLevel


class PremiumSupport(commands.Cog):
    """Special support for Premium members."""

    def __init__(self, bot: ModmailBot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

        self.roles = []
        self.message = ""
        self.mention = ""
        self.category = 0

        asyncio.create_task(self._set_val())

    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"},
            {
                "$set": {
                    "roles": self.roles,
                    "message": self.message,
                    "mention": self.mention,
                    "category": self.category,
                }
            },
            upsert=True,
        )

    async def _set_val(self):
        config = await self.db.find_one({"_id": "config"})

        if config:
            self.roles = config.get("roles", [])
            self.message = config.get("message", "")
            self.mention = config.get("mention", "")
            self.category = config.get("category", "")

    @commands.Cog.listener()
    async def on_thread_ready(self, thread, creator, category, initial_message):
        if isinstance(thread.recipient, int):
            recipient_id = thread.recipient
        else:
            recipient_id = thread.recipient.id
        recipient = await self.bot.modmail_guild.fetch_member(recipient_id)
        premium = False
        for role in recipient.roles:
            if role.id in self.roles:
                premium = True

        if not premium:
            return

        class Author:
            roles = []
            id = recipient_id

        class Msg:
            content = self.message
            author = Author
            created_at = datetime.datetime.now()
            id = initial_message.id
            attachments = []
            stickers = []

        if Msg.content:
            await thread.send(Msg, destination=recipient, from_mod=True, anonymous=True)

        if self.mention:
            await thread.channel.send(self.mention)

        if self.category:
            await thread.channel.move(
                end=True,
                category=discord.utils.get(
                    thread.channel.guild.channels, id=self.category
                ),
                reason="Premium support plugin.",
            )

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True, aliases=["pc"])
    async def premiumconfig(self, ctx):
        """
        Config your premium support!

        To view your settings, use [p]premiumconfig.

        To edit, use [p]premiumconfig <thingyouwanttoedit> <newvalue>
        """
        embed = discord.Embed(colour=self.bot.main_color)
        embed.set_author(
            name="Premium Support Configurations:", icon_url=self.bot.user.avatar.url
        )
        embed.add_field(name="Premium Roles", value=f"`{self.roles}`", inline=False)
        embed.add_field(
            name="Premium Message",
            value=f"{'`' + self.message + '`' if self.message else 'None'}",
            inline=False,
        )
        embed.add_field(
            name="Mention Message",
            value=f"{'`' + self.mention + '`' if self.message else 'None'}",
            inline=False,
        )
        embed.add_field(
            name="Premium Category", value=f"`{self.category}`", inline=False
        )
        embed.set_footer(
            text=f"To change use {self.bot.prefix}premiumconfig <thing> <value>. Use {self.bot.prefix}help premiumconfig for the list of things you can change."
        )
        await ctx.send(embed=embed)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @premiumconfig.command(aliases=["role"])
    async def roles(self, ctx, roles: commands.Greedy[discord.Role]):
        """Set premium roles."""
        self.roles = [role.id for role in roles]
        await self._update_db()
        await ctx.send(f"Premium roles set to: `{self.roles}`")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @premiumconfig.command()
    async def message(self, ctx, *, message):
        """Set premium message reply."""
        self.message = message
        await self._update_db()
        await ctx.send(f"Premium message set to: `{self.message}`")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @premiumconfig.command()
    async def mention(self, ctx, *, message):
        """Set on_premium mention message."""
        self.mention = message
        await self._update_db()
        await ctx.send(f"Mention message set to: `{self.mention}`")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @premiumconfig.command()
    async def category(self, ctx, category_id: int = 0):
        """Set premium category id. 0 equals none."""
        self.category = category_id
        await self._update_db()
        await ctx.send(f"Premium category set to: `{self.category}`")


async def setup(bot):
    await bot.add_cog(PremiumSupport(bot))
