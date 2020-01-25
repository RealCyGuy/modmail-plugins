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
            {"$set": {"suggestion-channel": {"channel": str(channel)}}},
            upsert=True,
        )

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        async with ctx.channel.typing():
            config = await self.coll.find_one({"_id": "config"})
            if config is None:
                await ctx.send('Suggestion channel not set.')
            else:
                channel = config["suggestion-channel"]["channel"]

                embed=discord.Embed(title=suggestion, color=0x71b8d7)
                embed.set_author(name=f"Suggestion by {ctx.author}:", icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Suggest(bot))