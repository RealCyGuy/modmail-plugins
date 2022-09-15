import discord
from discord.ext import commands


class AnigameChannels(commands.Cog):
    """
    Automatically rename #anigame-inactive to #anigame-active during battles!
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (
            message.author.id == 571027211407196161
            and message.embeds
            and message.channel.name in ["anigame-inactive", "anigame-active"]
        ):
            embed = message.embeds[0]
            if embed.title.startswith("**__Challenging "):
                await message.channel.edit(name="anigame-active")
            elif embed.title.startswith("**Victory") or embed.title.startswith(
                "**Defeated"
            ):
                await message.channel.edit(name="anigame-inactive")


def setup(bot):
    bot.add_cog(AnigameChannels(bot))
