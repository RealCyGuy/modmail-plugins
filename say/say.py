import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def say2(self, ctx, *, message):
        """ModMail says what you want it to say."""
        await ctx.send(message.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere"))
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(Say(bot))
