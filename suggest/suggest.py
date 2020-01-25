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
        embed=discord.Embed(title=f'Set suggestion channel to {channel}.', color=0x15d649)
        embed.set_author(name="Success!")
        embed.set_footer(text="Task succeeded successfully.")
        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, *, suggestion):
        async with ctx.channel.typing():
            config = await self.coll.find_one({"_id": "config"})
            if config is None:
                await ctx.send('Suggestion channel not set.')
            else:
                channel = client.get_channel(int(config["suggestion-channel"]["channel"]))

                embed=discord.Embed(title=suggestion, color=0x71b8d7)
                embed.set_author(name=f"Suggestion by {ctx.author}:", icon_url=ctx.author.avatar_url)
                await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(Suggest(bot))