import discord
from discord.ext import commands


class KarutaKeqingAutoReact(commands.Cog):
    """
    Reacts to karuta character lookup and collection for keqing bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == 646937666251915264 and message.embeds:
            embed = message.embeds[0]
            if embed.title.startswith("Card Collection"):
                await message.add_reaction("\N{PENCIL}")
            elif embed.title.startswith("Character Lookup"):
                await message.add_reaction("\N{PAINTBRUSH}")


def setup(bot):
    bot.add_cog(KarutaKeqingAutoReact(bot))
