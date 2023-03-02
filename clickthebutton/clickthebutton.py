import asyncio
import math
import random
import sys
import time
import uuid
from collections import OrderedDict
from datetime import timedelta

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel
from .responses import random_cooldown_over, random_emoji, random_fought_off


def event(text, content="") -> str:
    content = content.split("\n")
    content.append(f"<t:{int(time.time())}:f>: {text}")
    while len("\n".join(content)) > 2000:
        content.pop(0)
    return "\n".join(content)


class ClickTheButton(commands.Cog):
    """
    Clicking button game. Use ?startbutton to get started.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.api.db.plugins["ClickTheButton2"]
        self.view = None
        self.message = None
        self.leaderboard = {}
        self.custom_id = ""
        self.clickers = OrderedDict()
        self.interaction_message = None

    def get_sorted_leaderboard(self):
        return sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)

    async def create_leaderboard_embed(self, cooldown=0):
        embed = discord.Embed(
            title="Click the button leaderboard!",
            description="Press the button that has a random global cooldown! Everytime you press it, you get one "
            "click (point).\n\n",
            colour=random.randint(0, 16777215),
        )
        sorted_leaderboard = self.get_sorted_leaderboard()
        leaderboard_text = ""
        total_clicks = sum(self.leaderboard.values())
        for n in range(1, 11):
            stats = ""
            if len(sorted_leaderboard) >= n:
                user = sorted_leaderboard[n - 1]
                stats = f"<@{user[0]}> - {user[1]} click{'s' if user[1] > 1 else ''} ({(user[1] / total_clicks * 100):.2f}%)"
            leaderboard_text += str(n) + ". " + stats + "\n"
        leaderboard_text += "\n"
        t = math.ceil(time.time())
        if cooldown:
            timestamp = t + cooldown
            leaderboard_text += (
                f"The button will be re-enabled <t:{timestamp}:R> (<t:{timestamp}:T>)!"
            )
        else:
            leaderboard_text += (
                f"You can click the button! (You could've since <t:{t}:F>.)"
            )
        embed.description += leaderboard_text
        players = len(self.leaderboard)
        embed.set_footer(
            text=f"{players} player{'' if players == 1 else 's'} - {total_clicks} total clicks - by cyrus yip"
        )
        return embed

    async def cog_load(self):
        if self.view is None:
            config = await self.db.find_one({"_id": "config"})
            data = await self.db.find_one({"_id": "data"}) or {}
            self.leaderboard = data.get("leaderboard", {})
            if config:
                self.custom_id = config.get("custom_id")
                if self.custom_id:
                    self.view = PersistentView(self)
                    self.bot.add_view(self.view)
                    try:
                        self.message = (
                            await self.bot.get_guild(config["message"][0])
                            .get_channel(config["message"][1])
                            .fetch_message(config["message"][2])
                        )
                        await self.message.edit(
                            embed=await self.create_leaderboard_embed(), view=self.view
                        )
                    except:
                        pass

    async def cog_unload(self):
        if self.view:
            self.view.stop()
        try:
            await self.interaction_message.delete()
        except:
            pass
        try:
            del sys.modules[__name__[:-14] + "responses"]
        except:
            pass
        for task in asyncio.all_tasks():
            if self.view.id in task.get_name():
                try:
                    task.cancel()
                except:
                    pass

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def startbutton(self, ctx: commands.Context):
        """Starts a persistent view."""
        self.custom_id = str(uuid.uuid4())
        if self.view:
            self.view.stop()
        self.view = PersistentView(self)
        msg = await ctx.send(
            event("Click the button leaderboard was created!"),
            embed=await self.create_leaderboard_embed(),
            view=self.view,
        )
        await self.db.update_one(
            {"_id": "config"},
            {
                "$set": {
                    "custom_id": self.custom_id,
                    "message": [msg.guild.id, msg.channel.id, msg.id],
                }
            },
            upsert=True,
        )


class PersistentView(discord.ui.View):
    def __init__(self, cog: ClickTheButton):
        super().__init__(timeout=None)
        self.button.custom_id = cog.custom_id
        self.cog = cog

    async def do_stuff(
        self,
        interaction: discord.Interaction,
        user_id,
        points,
        cooldown,
        fought_off: str,
    ):
        rank = 0
        sorted_leaderboard = self.cog.get_sorted_leaderboard()
        for player in sorted_leaderboard:
            rank += 1
            if player[0] == user_id:
                break
        fought = ""
        clickers = list(self.cog.clickers.keys())
        clickers.remove(interaction.user.id)
        if clickers:
            winner_time = self.cog.clickers[interaction.user.id]
            mentions = ", ".join(
                f"<@{user_id}> ({int((self.cog.clickers[user_id] - winner_time) / timedelta(milliseconds=1))}ms)"
                for user_id in clickers
            )
            fought = f" {fought_off} {mentions} and"
        reaction = random_emoji()
        self.cog.interaction_message = await interaction.channel.send(
            content=f"{reaction} <@{user_id}>{fought} got a click!\n"
            f"You are now at {points} clicks and ranked #{rank} out of {len(self.cog.leaderboard)} players.",
            delete_after=max(5, cooldown - 5),
        )
        try:
            await self.cog.interaction_message.add_reaction(reaction)
        except:
            pass

    @discord.ui.button(
        label="Click to get a point!",
        style=discord.ButtonStyle.green,
    )
    async def button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(interaction.user.id)
        if interaction.user.id in self.cog.clickers:
            return await interaction.response.defer()
        if self.cog.clickers:
            self.cog.clickers[interaction.user.id] = interaction.created_at
            return await interaction.response.defer()
        self.cog.clickers[interaction.user.id] = interaction.created_at
        await interaction.response.defer()

        points = self.cog.leaderboard.get(user_id, 0) + 1
        self.cog.leaderboard[user_id] = points
        await self.cog.db.update_one(
            {"_id": "data"},
            {"$set": {"leaderboard": self.cog.leaderboard}},
            upsert=True,
        )
        button.style = discord.ButtonStyle.grey
        button.disabled = True
        cooldown = random.choices(
            [(0, 5), (6, 39), (40, 179), (180, 599), (600, 720)],
            cum_weights=[1, 2, 6, 8, 9],
        )[0]
        cooldown = random.randint(*cooldown)
        await asyncio.sleep(2)
        fought = ""
        fought_off = random_fought_off()
        if len(self.cog.clickers) >= 2:
            await asyncio.sleep(3)
            fought = f" {fought_off} {len(self.cog.clickers) - 1} and"
        await interaction.message.edit(
            content=event(
                f"{interaction.user.name}#{interaction.user.discriminator}{fought} is now at {points} clicks.",
                interaction.message.content,
            ),
            embed=await self.cog.create_leaderboard_embed(cooldown=cooldown),
            view=self,
        )
        asyncio.create_task(
            self.do_stuff(interaction, user_id, points, cooldown, fought_off)
        )
        if cooldown > 5:
            await asyncio.sleep(cooldown - 4)
            asyncio.create_task(
                interaction.channel.send(
                    random_cooldown_over(),
                    delete_after=0,
                )
            )
            await asyncio.sleep(4)
        else:
            await asyncio.sleep(cooldown)
        button.style = discord.ButtonStyle.green
        button.disabled = False
        self.cog.clickers = OrderedDict()
        await interaction.message.edit(
            embed=await self.cog.create_leaderboard_embed(),
            view=self,
        )


async def setup(bot):
    await bot.add_cog(ClickTheButton(bot))
