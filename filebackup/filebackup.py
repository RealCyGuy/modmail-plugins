import asyncio
import json

import discord
from discord import DMChannel
from discord.ext import commands
from discord.mixins import Hashable

from bot import ModmailBot
from core import checks
from core.clients import MongoDBClient
from core.models import PermissionLevel


async def append_log_with_backup(
    self: MongoDBClient,
    message: discord.Message,
    *,
    message_id: str = "",
    channel_id: str = "",
    type_: str = "thread_message",
):
    bot: ModmailBot = self.bot
    cog = bot.get_cog("FileBackup")
    if (
        not message.attachments
        or type(cog) is not FileBackup
        or not (config := cog.get_config())
        or not (backup_channel_id := config.get("backup_channel"))
        or not bot.modmail_guild
        or not (backup_channel := bot.modmail_guild.get_channel(backup_channel_id))
        or (
            not config.get("backup_non_staff", True)
            and (isinstance(message.channel, DMChannel))
        )
    ):
        return await self.old_append_log(
            message, message_id=message_id, channel_id=channel_id, type_=type_
        )

    channel_id = str(channel_id) or str(message.channel.id)
    message_id = str(message_id) or str(message.id)

    attachements = []
    for a in message.attachments:
        url = a.url
        try:
            msg = await backup_channel.send(
                f"File sent by {message.author.mention} ({message.author.id}) in <#{channel_id}> ({channel_id}).",
                file=await a.to_file(),
                allowed_mentions=discord.AllowedMentions.none()
            )
            url = msg.attachments[0].url
        except:
            pass
        attachements.append(
            {
                "id": a.id,
                "filename": a.filename,
                "is_image": a.width is not None,
                "size": a.size,
                "url": url,
            }
        )

    data = {
        "timestamp": str(message.created_at),
        "message_id": message_id,
        "author": {
            "id": str(message.author.id),
            "name": message.author.name,
            "discriminator": message.author.discriminator,
            "avatar_url": message.author.display_avatar.url,
            "mod": not isinstance(message.channel, DMChannel),
        },
        "content": message.content,
        "type": type_,
        "attachments": attachements,
    }

    return await self.logs.find_one_and_update(
        {"channel_id": channel_id}, {"$push": {"messages": data}}, return_document=True
    )


class FakeChannel(discord.abc.Messageable, discord.abc.GuildChannel, Hashable):
    """A fake channel to capture the embed sent by the help command."""

    def __init__(self):
        super().__init__()
        self.embed = None

    async def send(self, *args, **kwargs):
        self.embed = kwargs["embed"]


class FileBackup(commands.Cog):
    """
    Automatically backup attachements sent in threads to a Discord channel.

    This is for viewing attachments in the logviewer after the thread channel has been deleted.
    """

    def __init__(self, bot: ModmailBot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.config = {}

        MongoDBClient.old_append_log = MongoDBClient.append_log
        MongoDBClient.append_log = append_log_with_backup

        asyncio.create_task(self._fetch_db())

    def get_config(self):
        return self.config

    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"config": self.config}},
            upsert=True,
        )

    async def _fetch_db(self):
        config = await self.db.find_one({"_id": "config"})
        if config:
            self.config = config.get("config", {})

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True)
    async def backupconfig(self, ctx: commands.Context):
        """
        Configure FileBackup settings!

        To view your settings, use [p]backupconfig.
        To edit, use [p]backupconfig <thingyouwanttoedit> <newvalue>
        """
        embed = discord.Embed(colour=self.bot.main_color)
        embed.set_author(
            name="FileBackup Config", icon_url=self.bot.user.display_avatar.url
        )
        embed.description = "```json\n" + json.dumps(self.config, indent=2) + "\n```"

        fake_channel = FakeChannel()
        help_command = self.bot.help_command.copy()
        help_command.context = ctx
        help_command.get_destination = lambda: fake_channel
        await help_command.send_group_help(ctx.command)

        await ctx.send(embeds=[embed, fake_channel.embed])

    @checks.has_permissions(PermissionLevel.ADMIN)
    @backupconfig.command()
    async def channel(
        self, ctx: commands.Context, *, channel: discord.TextChannel = None
    ):
        """Set the channel where attachements are backed up. Leave empty to disable."""
        if self.bot.modmail_guild != ctx.guild:
            return await ctx.send(
                "You can only set the backup channel in your modmail guild!"
            )
        if channel is None:
            self.config.pop("backup_channel", None)
            await self._update_db()
            await ctx.send(
                "Unset backup channel. Files won't be backed up anymore!\n"
                f"To set a channel, run `{self.bot.prefix}backupconfig channel <new channel>`"
            )
        else:
            self.config["backup_channel"] = channel.id
            await self._update_db()
            await ctx.send(f"Backup channel set to: `{channel.id}`")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @backupconfig.command()
    async def nonstaff(self, ctx: commands.Context, *, value: bool):
        """Toggle if attachements from non-staff should be backed up. Defaults to true."""
        self.config["backup_non_staff"] = value
        await self._update_db()
        await ctx.send(f"Backup non-staff set to: `{value}`")


async def setup(bot):
    await bot.add_cog(FileBackup(bot))
