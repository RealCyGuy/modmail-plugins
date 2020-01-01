import discord
from discord.ext import commands

class Say2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def say2(self, ctx, *, message):
        await ctx.send(message)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Say2(bot))
