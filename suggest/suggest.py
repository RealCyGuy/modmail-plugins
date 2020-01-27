import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class Suggest(commands.Cog):
    """
    Let's you send a suggestion to a designated channel.
    """
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

    @commands.command(aliases = ['ssc'])
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setsuggestchannel(self, ctx, channel: discord.TextChannel):
        """
        Set the channel where suggestions go.
        """
        await self.coll.find_one_and_update(
            {"_id": "config"},
            {"$set": {"suggestion-channel": {"channel": str(channel.id)}}},
            upsert=True,
        )
        embed=discord.Embed(title=f'Set suggestion channel to #{channel}.', color=0x4dff73)
        embed.set_author(name="Success!")
        embed.set_footer(text="Task succeeded successfully.")
        await ctx.send(embed=embed)

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def suggestchannel(self, ctx):
        """Displays the suggestion channel."""
        config = await self.coll.find_one({"_id": "config"})
        suggestion_channel = self.bot.get_channel(int(config["suggestion-channel"]["channel"]))
        embed=discord.Embed(title=f'The suggestion channel is: #{suggestion_channel}', description='To change it, use [p]setsuggetchannel.',color=0x4dff73)
        await ctx.send(embed=embed)

    @checks.has_permissions(PermissionLevel.MOD)
    @commands.group(invoke_without_command=True)
    async def suggestmod(self, ctx: commands.Context):
        """Let's you block and unblock people from using the suggest command."""
        await ctx.send_help(ctx.command)

    @suggestmod.command(aliases = ['ban'])
    @checks.has_permissions(PermissionLevel.MOD)
    async def block(self, ctx, user: discord.User):
        """
        Block a user from using the suggest command.

        **Examples:**
        [p]suggestmod block @RealCyGuy
        [p]suggestmod ban 543225108135673877
        """
        mod = await self.coll.find_one({"_id": "mod"})
        userid = str(user.id)
        if mod is None:
            await self.coll.find_one_and_update(
                {"_id": "banned"},
                {"$set": {"users": list()}},
                upsert=True
            )
        mod = await self.coll.find_one({"_id": "mod"})
        self.banlist = mod.get("users", list())
        if userid not in self.banlist:
            self.banlist.append(userid)
            await self.coll.find_one_and_update(
                {"_id": "mod"},
                {"$set": {"banned": {"users": self.banlist}}},
                upsert=True,
            )

    @suggestmod.command(aliases = ['unban'])
    @checks.has_permissions(PermissionLevel.MOD)
    async def unblock(self, ctx, user: discord.User):
        """
        Unblock a user from using the suggest command.

        **Examples:**
        [p]suggestmod unblock @RealCyGuy
        [p]suggestmod unban 543225108135673877
        """
        mod = await self.coll.find_one({"_id": "mod"})
        userid = str(user.id)
        if mod is None:
            await self.coll.find_one_and_update(
                {"_id": "banned"},
                {"$set": {"users": list()}},
                upsert=True
            )
        mod = await self.coll.find_one({"_id": "mod"})
        self.banlist = mod.get("users", list())
        if userid in self.banlist:
            self.banlist.remove(userid)
            await self.coll.find_one_and_update(
                {"_id": "mod"},
                {"$set": {"banned": {"users": self.banlist}}},
                upsert=True,
            )

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        """
        Suggest something!
        """
        async with ctx.channel.typing():
            config = await self.coll.find_one({"_id": "config"})
            if config is None:
                embed=discord.Embed(title="Suggestion channel not set.", color=self.bot.error_colour)
                embed.set_author(name="Error.")
                embed.set_footer("Task failed successfully.")
                await ctx.send(embed=embed)
            else:
                suggestion_channel = self.bot.get_channel(int(config["suggestion-channel"]["channel"]))

                embed=discord.Embed(title=suggestion, color=0x59e9ff)
                embed.set_author(name=f"Suggestion by {ctx.author}:", icon_url=ctx.author.avatar_url)
                await suggestion_channel.send(embed=embed)
                await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

def setup(bot):
    bot.add_cog(Suggest(bot))