import discord
from discord.ext import commands
import aiohttp

class Hastebin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = 'haste')
    async def hastebin(self, ctx, *, text):
        """Puts text in hastebin"""
        async with aiohttp.ClientSession() as session:
            async with session.post("https://hastebin/documents", data=text) as response:
                json = await response.json
                await ctx.send(f"https://hastebin.com/{json['key']}")

def setup(bot):
    bot.add_cog(Hastebin(Bot))