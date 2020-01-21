import discord
from discord.ext import commands

class ReactOnPing(commands.Cog):
    """Reacts with a ping emoji when someone gets pinged."""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        emoji = self.bot.get_emoji(667602017530937354)
        if '<@' in message.content.upper():
            await message.add_reaction(emoji)
            await message.channel.send(list(client.get_all_emojis()))

def setup(bot):
    bot.add_cog(ReactOnPing(bot))