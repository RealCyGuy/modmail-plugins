import discord
from discord.ext import commands

class Banana(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'banana' in message:
            await message.channel.send('hi')

def setup(bot):
    bot.add_cog(Banana(bot))