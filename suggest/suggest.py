# registry: suggest

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

        bot.loop.create_task(self._set_mod_val())

    async def _update_mod_db(self):
        await self.coll.find_one_and_update(
            {"_id": "mod"}, {"$set": {"banlist": self.banlist}}, upsert=True,
        )

    async def _set_mod_val(self):
        mod = await self.coll.find_one({"_id": "mod"})

        if mod is None:
            return

        self.banlist = mod["banlist"]

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.member)
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
                        title="Suggestion channel not set.", color=self.bot.error_color
                    )
                    embed.set_author(name="Error.")
                    embed.set_footer(text="Task failed successfully.")
                    await ctx.send(embed=embed)
                else:
                    suggestion_channel = self.bot.get_channel(
                        int(config["suggestion-channel"]["channel"])
                    )
                    suggestions = await self.coll.find_one({"_id": "suggestions"}) or {}
                    next_id = suggestions.get("next_id", 1)

                    embed = discord.Embed(color=0x59E9FF)
                    embed.set_author(name=f"Suggestion #{next_id}: Waiting")
                    embed.set_thumbnail(url=ctx.author.avatar.url)
                    embed.add_field(
                        name="Author",
                        value=f"{ctx.author.mention} (ID: {ctx.author.id})",
                        inline=False,
                    )
                    embed.add_field(name="Suggestion", value=suggestion, inline=False)
                    message = await suggestion_channel.send(embed=embed)
                    await self.coll.find_one_and_update(
                        {"_id": "suggestions"},
                        {
                            "$set": {
                                "next_id": next_id + 1,
                                str(next_id): {"message_id": message.id,},
                            }
                        },
                        upsert=True,
                    )
                    re = config.get("reaction-emojis")
                    if re:
                        for r in re.get("emojis", []):
                            await message.add_reaction(
                                discord.utils.get(message.guild.emojis, id=r)
                            )
                            await asyncio.sleep(0.1)
                    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        else:
            await ctx.send(
                embed=discord.Embed(
                    color=self.bot.error_color,
                    title=f"You have been blocked, {ctx.author.name}#{ctx.author.discriminator}.",
                    description=f"Reason: {self.banlist[str(ctx.author.id)]}",
                )
            )

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def approve(self, ctx, suggestion_id: int, *, message=None):
        """
        Approve an suggestion.

        **Usage**:
        [p]approve 5 That's a good idea and will be implemented soon (trademarked).
        [p]approve 456 I agree.
        """
        await ctx.message.delete()
        suggestions = await self.coll.find_one({"_id": "suggestions"})
        suggestion = suggestions.get(str(suggestion_id), None)
        if not suggestion:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"Suggestion id #{suggestion_id} not found.",
                description="Try something else lol.",
            )
            return await ctx.send(embed=embed)
        s_message = None
        for channel in ctx.guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            try:
                s_message = await channel.fetch_message(suggestion["message_id"])
            except discord.NotFound:
                continue
        if not s_message:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"Message not found.",
                description="Make sure it's not deleted and that I have permissions to access it.",
            )
            return await ctx.send(embed=embed)
        embed = s_message.embeds[0]
        fields = len(embed.fields)
        embed.color = discord.Colour.green()
        embed.set_author(name=f"Suggestion #{suggestion_id}: Approved")
        if fields > 2:
            embed.remove_field(2)
        if fields == 4:
            embed.insert_field_at(
                index=2,
                name="Response",
                value=message if message else "No response given.",
                inline=False,
            )
        else:
            embed.add_field(
                name="Response",
                value=message if message else "No response given.",
                inline=False,
            )
        votes = ""
        for reaction in s_message.reactions:
            votes += f"{reaction.emoji} **- {reaction.count -1 if reaction.me else reaction.count }**\n"
        if votes:
            embed.add_field(name="Votes", value=votes, inline=False)
        await s_message.edit(embed=embed)
        await s_message.clear_reactions()

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def deny(self, ctx, suggestion_id: int, *, message=None):
        """
        Deny an suggestion.

        **Usage**:
        [p]deny 27 That wouldn't work due to the way the thing in the works in contrast with the other thing.
        [p]deny 78 You're stupid.
        """
        await ctx.message.delete()
        suggestions = await self.coll.find_one({"_id": "suggestions"})
        suggestion = suggestions.get(str(suggestion_id), None)
        if not suggestion:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"Suggestion id #{suggestion_id} not found.",
                description="Try something else lol.",
            )
            return await ctx.send(embed=embed)
        s_message = None
        for channel in ctx.guild.channels:
            if not isinstance(channel, discord.TextChannel):
                continue
            try:
                s_message = await channel.fetch_message(suggestion["message_id"])
            except discord.NotFound:
                continue
        if not s_message:
            embed = discord.Embed(
                colour=self.bot.error_color,
                title=f"Message not found.",
                description="Make sure it's not deleted and that I have permissions to access it.",
            )
            return await ctx.send(embed=embed)
        embed = s_message.embeds[0]
        fields = len(embed.fields)
        embed.color = discord.Colour.red()
        embed.set_author(name=f"Suggestion #{suggestion_id}: Denied")
        if fields > 2:
            embed.remove_field(2)
        if fields == 4:
            embed.insert_field_at(
                index=2,
                name="Response",
                value=message if message else "No response given.",
                inline=False,
            )
        else:
            embed.add_field(
                name="Response",
                value=message if message else "No response given.",
                inline=False,
            )
        votes = ""
        for reaction in s_message.reactions:
            votes += f"{reaction.emoji} **- {reaction.count - 1 if reaction.me else reaction.count}**\n"
        if votes:
            embed.add_field(name="Votes", value=votes, inline=False)
        await s_message.edit(embed=embed)
        await s_message.clear_reactions()

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setsuggestchannel(self, ctx, *, channel: discord.TextChannel):
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

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setemojis(self, ctx, *emojis: discord.Emoji):
        """
        Set emojis to react to each suggestion with.

        **Usage**:
        [p]setemojis \N{WHITE HEAVY CHECK MARK} \N{CROSS MARK}
        [p]se (custom emojis)
        """
        await self.coll.find_one_and_update(
            {"_id": "config"},
            {"$set": {"reaction-emojis": {"emojis": [i.id for i in emojis]}}},
            upsert=True,
        )
        embed = discord.Embed(title=f"Set emojis.", color=0x4DFF73)
        embed.set_author(name="Success!")
        embed.set_footer(text="Task succeeded successfully.")
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
                colour=self.bot.main_color,
                title=f"{user.name}#{user.discriminator} is now unblocked.",
            )

        await self._update_mod_db()
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Suggest(bot))
