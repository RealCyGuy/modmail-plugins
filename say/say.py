import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def say(self, ctx, *, message):
        await ctx.send(message)
        await delete(ctx.message)

def setup(bot):
    bot.add_cog(Say(bot))