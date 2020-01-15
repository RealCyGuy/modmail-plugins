import discord
from discord.ext import commands

class Banana(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if 'BANANA' in message.content.upper():
            await message.add_reaction('\N{BANANA}')

def setup(bot):
    bot.add_cog(Banana(bot))