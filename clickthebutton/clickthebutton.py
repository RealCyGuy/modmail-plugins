import asyncio
import random
import time

import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, Interaction

from core import checks
from core.models import PermissionLevel


class ClickTheButton(commands.Cog):
    """
    Clicking button game. Use [p]startbutton to get started.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.leaderboard = {}
        self.message_id = 0
        self.winner_role_id = 0
        self.winner_id = 0
        self.started = False

    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"}, {"$set": {"message": self.message_id, "winner_role": self.winner_role_id}}, upsert=True,
        )
        await self.db.find_one_and_update(
            {"_id": "data"}, {"$set": {"leaderboard": self.leaderboard}}, upsert=True,
        )

    async def _get_db(self):
        config = await self.db.find_one({"_id": "config"})
        data = await self.db.find_one({"_id": "data"})

        if config is None:
            await self.db.find_one_and_update(
                {"_id": "config"}, {"$set": {"mesasage": 0, "winner_role": 0}}, upsert=True,
            )
            config = await self.db.find_one({"_id": "config"})

        if data is None:
            await self.db.find_one_and_update(
                {"_id": "data"}, {"$set": {"leaderboard": dict(), "winner": 0}}, upsert=True
            )

            data = await self.db.find_one({"_id": "data"})

        self.message_id = config.get("message", 0)
        self.winner_role_id = config.get("winner_role", 0)
        self.leaderboard = data.get("leaderboard", {})
        self.winner_id = data.get("winner", 0)

    def get_sorted_leaderboard(self):
        return sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)

    async def startup(self):
        if self.started:
            return
        self.started = True
        await self._get_db()
        DiscordComponents(self.bot)
        for channel in self.bot.get_all_channels():
            try:
                msg = await channel.fetch_message(self.message_id)
            except:
                continue
            if msg.author.id == self.bot.user.id:
                embed = await self.create_leaderboard_embed()
                await msg.edit(
                    embed=embed, components=[Button(label="Click to get a point!")]
                )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.startup()

    @commands.Cog.listener()
    async def on_plugins_ready(self):
        await self.startup()

    @commands.Cog.listener()
    async def on_button_click(self, interaction: Interaction):
        if interaction.message.id == self.message_id:
            points = self.leaderboard.get(str(interaction.author.id), 0)
            self.leaderboard[str(interaction.author.id)] = points + 1
            await self._update_db()
            rank = 0
            for player in self.get_sorted_leaderboard():
                rank += 1
                if int(player[0]) == interaction.author.id:
                    break
            await interaction.respond(
                content=f"You got a point! You are now at {self.leaderboard[str(interaction.author.id)]} points and "
                        f"ranked #{rank} out of {len(self.leaderboard)} players. "
            )
            cooldown = random.randint(60, 180)
            embed = await self.create_leaderboard_embed(cooldown=cooldown)
            await interaction.message.edit(
                embed=embed, components=[Button(label="On cooldown.", disabled=True)]
            )
            await asyncio.sleep(cooldown)
            embed = await self.create_leaderboard_embed()
            await interaction.message.edit(
                embed=embed, components=[Button(label="Click to get a point!")]
            )

    async def create_leaderboard_embed(self, cooldown=0):
        embed = discord.Embed(
            title="Click the button leaderboard!",
            description="Press the button that has a random global cooldown! Everytime you press it, you get one "
            "point.\n\n",
            colour=discord.Colour.from_rgb(191, 23, 252),
        )
        sorted_leaderboard = self.get_sorted_leaderboard()
        leaderboard_text = ""
        for n in range(1, 11):
            stats = ""
            if len(sorted_leaderboard) >= n:
                user = sorted_leaderboard[n - 1]
                stats = f"<@{user[0]}> - {user[1]} points"
            leaderboard_text += str(n) + ". " + stats + "\n"
        leaderboard_text += "\n"
        if cooldown:
            timestamp = int(time.time()) + cooldown
            leaderboard_text += f"The button will be re-enabled <t:{timestamp}:R>!"
        else:
            leaderboard_text += "You can click the button!"
        embed.description += leaderboard_text
        players = len(self.leaderboard)
        embed.set_footer(text=f"{players} player{'' if players == 1 else 's'} - by cyrus yip")
        return embed

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def startbutton(self, ctx):
        """
        This will place the leaderboard and game in the channel the command is used in.
        This will replace any previous one too.
        """
        embed = await self.create_leaderboard_embed()
        msg = await ctx.send(
            embed=embed, components=[Button(label="Click to get a point!")],
        )
        self.message_id = msg.id
        await self._update_db()


def setup(bot):
    bot.add_cog(ClickTheButton(bot))
