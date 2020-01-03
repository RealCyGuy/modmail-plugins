import discord
from discord.ext import commands
import asyncio

class dmallmembers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dmall(self, ctx, *, message):
        """
        Makes ModMail dm all members in the server.

        Usage: [prefix]dmall <message>
        """
        for x in message.guild.members:
            asyncio.sleep(1)
            membrr = x
            await membrr.send(message)



def setup(bot):
    bot.add_cog(dmallmembers(bot))