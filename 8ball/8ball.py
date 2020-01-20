import discord
from discord.ext import commands
import random
import magic8ball

class EightBall(commands.Cog):
    """
    Ask ModMail a question and get an answer from a ever-growing list of answers.

    Disclaimer: These answers are jokes and should be taken as jokes.
    For legal advice, talk to a lawyer.
    For general advice, don't take it from a bot.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['ateball', '8bl'])
    async def eightball(self, ctx, *, question):
        """
        Ask ModMail 8-Ball a question and get a response!

        Usage: [prefix]eightball <question>
        """
        embed=discord.Embed(title=f"Question by {ctx.author}:", description=question, color=0x51eaff)
        embed.set_author(name="8-Ball", url="https://github.com/realcyguy/modmail-plugins/", icon_url="https://media.istockphoto.com/photos/pool-ball-picture-id491993923?k=6&m=491993923&s=612x612&w=0&h=u6SNe9jYA1ZidZ_vfU1LHpaDVNnrbUFivOKxazcrNCI=")
        embed.add_field(name="Answer:", value=random.choice(magic8ball.list), inline=False)
        embed.set_footer(text="?plugin add realcyguy/modmail-plugins/8ball")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(EightBall(bot))
