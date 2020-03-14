import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel
import asyncio


class Suggest(commands.Cog):
    """
    Let's you send a suggestion to a designated channel.
    """

    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

        self.banlist = dict()

        asyncio.create_task(self._set_mod_val())

    async def _update_mod_db(self):
        await self.coll.find_one_and_update(
            {"_id": "mod"}, {"$set": {"banlist": self.banlist,}}, upsert=True,
        )

    async def _set_mod_val(self):
        mod = await self.coll.find_one({"_id": "mod"})

        if mod is None:
            return

        self.banlist = mod["banlist"]

    @commands.command()
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def suggest(self, ctx, *, suggestion):
        """
        Suggest something!

        **Usage**:
        [p]suggest more plugins!
        """
        if str(ctx.author.id) not in self.banlist:
            async with ctx.channel.typing():
                config = await self.coll.find_one({"_id": "config"})
                if config is None:
                    embed = discord.Embed(
                        title="Suggestion channel not set.", color=self.bot.error_colour
                    )
                    embed.set_author(name="Error.")
                    embed.set_footer(text="Task failed successfully.")
                    await ctx.send(embed=embed)
                else:
                    suggestion_channel = self.bot.get_channel(
                        int(config["suggestion-channel"]["channel"])
                    )

                    embed = discord.Embed(title=suggestion, color=0x59E9FF)
                    embed.set_author(
                        name=f"Suggestion by {ctx.author}:", icon_url=ctx.author.avatar_url
                    )
                    await suggestion_channel.send(embed=embed)
                    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        else:
            await ctx.send(embed=discord.Embed(color=self.bot.error_color, title=f"You have been blocked, {ctx.author.name}#{ctx.author.discriminator}.", description=f"Reason: {self.banlist[str(ctx.author.id)]}"))

    @commands.command(aliases=["ssc"])
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setsuggestchannel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel where suggestions go.

        **Usage**:
        [p]setsuggestchannel #suggestions
        [p]ssc suggestions
        [p]ssc 515085600047628288
        """
        await self.coll.find_one_and_update(
            {"_id": "config"},
            {"$set": {"suggestion-channel": {"channel": str(channel.id)}}},
            upsert=True,
        )
        embed = discord.Embed(
            title=f"Set suggestion channel to #{channel}.", color=0x4DFF73
        )
        embed.set_author(name="Success!")
        embed.set_footer(text="Task succeeded successfully.")
        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def suggestchannel(self, ctx):
        """Displays the suggestion channel."""
        config = await self.coll.find_one({"_id": "config"})
        suggestion_channel = self.bot.get_channel(
            int(config["suggestion-channel"]["channel"])
        )
        embed = discord.Embed(
            title=f"The suggestion channel is: #{suggestion_channel}",
            description="To change it, use [p]setsuggestchannel.",
            color=0x4DFF73,
        )
        await ctx.send(embed=embed)

    @checks.has_permissions(PermissionLevel.MOD)
    @commands.group(invoke_without_command=True)
    async def suggestmod(self, ctx: commands.Context):
        """Let's you block and unblock people from using the suggest command."""
        await ctx.send_help(ctx.command)

    @suggestmod.command(aliases=["ban"])
    @checks.has_permissions(PermissionLevel.MOD)
    async def block(self, ctx, user: discord.User, *, reason="Reason not specified."):
        """
        Block a user from using the suggest command.

        **Examples:**
        [p]suggestmod block @RealCyGuy for abuse!
        [p]suggestmod ban 543225108135673877 `cause he's the same person!!!
        """
        if str(user.id) in self.banlist:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"{user.name}#{user.discriminator} is already blocked.",
                description=f"Reason: {self.banlist[str(user.id)]}",
            )
        else:
            self.banlist[str(user.id)] = reason
            embed = discord.Embed(
                colour=self.bot.main_color,
                title=f"{user.name}#{user.discriminator} is now blocked.",
                description=f"Reason: {reason}",
            )

        await self._update_mod_db()
        await ctx.send(embed=embed)

    @suggestmod.command(aliases=["unban"])
    @checks.has_permissions(PermissionLevel.MOD)
    async def unblock(self, ctx, user: discord.User):
        """
        Unblock a user from using the suggest command.

        **Examples:**
        [p]suggestmod unblock @RealCyGuy
        [p]suggestmod unban 543225108135673877
        """
        if str(user.id) not in self.banlist:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"{user.name}#{user.discriminator} is not blocked.",
                description=f"Reason: {self.banlist[str(user.id)]}",
            )
        else:
            self.banlist.pop(str(user.id))
            embed = discord.Embed(
                colour=self.bot.main_color, title=f"{user.name}#{user.discriminator} is now unblocked."
            )

        await self._update_mod_db()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Suggest(bot))
