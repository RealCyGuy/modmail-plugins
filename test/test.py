from discord.ext import commands

from core import checks
from core._color_data import ALL_COLORS
from core.models import PermissionLevel

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.content)

    @commands.command()
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def say(self, ctx, *, message):
        """
        Hey.
        """
        await ctx.send(message)

def setup(bot):
    bot.add_cog(Say(bot))
