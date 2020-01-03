import discord
from discord.ext import commands
import random

class 8ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    balllist = [
        'Yes.',
        'No.',
        'Of course.',
        'Good luck making that happen.',
        'It may happen.',
        'The chance of that happening is as likely as dolphins singing Happy Birthday all of a sudden.',
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
        'I see \'Yes\' in your future.'
    ]

    @commands.command()
    async def eightball(self, ctx, *, question):
        """Ask ModMail 8 Ball a question."""
        choice = random.choice(balllist)
        await ctx.send(f'Question: {question}\nAnswer: {choice}')

def setup(bot):
    bot.add_cog(8ball(bot))
