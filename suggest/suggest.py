import discord
from discord.ext import commands
from core import checks
from core.models import PermissionLevel

class Suggest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)

    @commands.command(aliases = ['ssc'])
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setsuggestchannel(self, ctx, channel: discord.TextChannel):
        await self.coll.find_one_and_update(
            {"_id": "config"},
            {"$set": {"suggestion-channel": {"channel": str(channel.id)}}},
            upsert=True,
        )
        embed=discord.Embed(title=f'Set suggestion channel to {channel}.', color=0x4dff73)
        embed.set_author(name="Success!")
        embed.set_footer(text="Task succeeded successfully.")
        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
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