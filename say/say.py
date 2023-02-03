from discord.ext import commands


class Say(commands.Cog):
    """A simple say command that removes everyone/here mentions."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say2(self, ctx, *, message):
        """Modmail says what you want it to say."""
        await ctx.send(
            message.replace("@everyone", "@\u200beveryone").replace(
                "@here", "@\u200bhere"
            )
        )
        await ctx.message.delete()


async def setup(bot):
    await bot.add_cog(Say(bot))
