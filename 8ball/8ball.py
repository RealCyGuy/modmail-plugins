import discord
from discord.ext import commands
import random

class eightball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    balllist = [
        'Yes.',
        'No.',
        'Of course.',
        'Good luck making that happen.',
        'It may happen.',
        'The chance of that happening is as likely as dolphins singing \'Happy Birthday\' all of a sudden.',
        'No, just... no.',
        'The magic sources say yes, don\'t ask me who they are!',
        'Ask again later, or never, it is not my decision.',
        'Outlook good.',
        'Seems nice.',
        'Ask again later.',
        'Concentrate and ask again.',
        'It might be yes, but how am I supposed to know!?',
        'Don\'t count on it.',
        'Maybe yes, maybe no.',
        'Yes - definitely.',
        'No - definitely not.',
        'Why are you asking me?',
        'Noooooooooooooooooooooooooooo.',
        'Error 404, response not found. Ask again later.',
        'I see \'Yes\' in your future.',
        'Only you know the answer... unless someone else knows.',
        'Why are you asking me questions, don\'t you have something better to do?',
        'The answer you are seeking is not available at the moment.',
        'Definitely, no.',
        'Stars aligned, I don\'t know what that means',
        'Saturn is bright today (or night).',
        'You think I\'m a magic 8 ball or something?',
        'Yes, yes, yes yes yes. The gods say: no.',
        'Yes sir. (or ma\'am or whatever you prefered to be called.)',
        '\"Bzzt- We got incoming. New message. \"What is it?\" \"No.\""',
        'Watermelons.'
    ]

    @commands.command()
    async def eightball(self, ctx, *, question):
        """
        Ask ModMail 8-Ball a question and get a response!
        """
        choice = random.choice(self.balllist)
        embed=discord.Embed(title="Question:", description=question, color=0x51eaff)
        embed.set_author(name="8-Ball", url="https://github.com/realcyguy/modmail-plugins/", icon_url="https://media.istockphoto.com/photos/pool-ball-picture-id491993923?k=6&m=491993923&s=612x612&w=0&h=u6SNe9jYA1ZidZ_vfU1LHpaDVNnrbUFivOKxazcrNCI=")
        embed.add_field(name="Answer:", value=choice, inline=False)
        embed.set_footer(text="?plugin add realcyguy/modmail-plugins/8ball")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(eightball(bot))
