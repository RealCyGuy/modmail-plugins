import asyncio
import math
import os
import random
import sys
import time
import uuid
from collections import OrderedDict

import discord
import motor.motor_asyncio
from discord.ext import commands
from matplotlib import font_manager

from core import checks
from core.models import PermissionLevel

from .responses import random_divider
from .utils import event
from .views import PersistentView


class ClickTheButton(commands.Cog):
    """
    Clicking button game. Use ?startbutton to get started.
    """

    def __init__(self, bot):
        self.bot = bot
        self.db: motor.motor_asyncio.AsyncIOMotorCollection = bot.api.db.plugins[
            "ClickTheButton2"
        ]
        self.dbGraph: motor.motor_asyncio.AsyncIOMotorCollection = bot.api.db.plugins[
            "ClickTheButton2Graph"
        ]
        self.view = None
        self.message = None
        self.leaderboard = {}
        self.custom_id = ""
        self.clickers = OrderedDict()
        self.streak = []
        self.delete_messages = {}

        self.winner_role_id = 0

    def delete_after(self, message: discord.Message, delay: int):
        self.delete_messages[message.id] = message

        async def delete(delay: int):
            await asyncio.sleep(delay)
            try:
                await message.delete()
            except discord.HTTPException:
                pass
            del self.delete_messages[message.id]

        asyncio.create_task(delete(delay))

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
        t = math.floor(time.time())
        if cooldown:
            timestamp = t + cooldown + 1
            leaderboard_text += (
                f"The button will be re-enabled <t:{timestamp}:R> (<t:{timestamp}:T>)!"
            )
        else:
            leaderboard_text += (
                f"You can click the button! (You could've since <t:{t}:F>.)"
            )
        embed.description += leaderboard_text
        players = len(self.leaderboard)
        divider = random_divider()
        embed.set_footer(
            text=f"{players} player{'' if players == 1 else 's'} {divider} {total_clicks} total clicks {divider} by cyrus yip"
        )
        return embed

    async def cog_load(self):
        for font in font_manager.findSystemFonts(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
        ):
            font_manager.fontManager.addfont(font)
        if self.view is None:
            config = await self.db.find_one({"_id": "config"})
            data = await self.db.find_one({"_id": "data"}) or {}
            self.leaderboard = data.get("leaderboard", {})
            if config:
                self.winner_role_id = config.get("winner_role", 0)
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
            streak_data = await self.db.find_one({"_id": "streak"})
            if streak_data:
                self.streak = [streak_data["id"], streak_data["streak"]]

    async def cog_unload(self):
        if self.view:
            self.view.stop()
        tasks = [message.delete() for message in self.delete_messages.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        for module in list(sys.modules.keys()):
            if module.startswith(
                ".".join(__name__.split(".")[:-1])
            ) and not module.endswith("clickthebutton"):
                try:
                    del sys.modules[module]
                except:
                    pass
        for task in asyncio.all_tasks():
            if self.view.id in task.get_name():
                try:
                    task.cancel()
                except:
                    pass
        if self.streak:
            await self.db.update_one(
                {"_id": "streak"},
                {"$set": {"id": self.streak[0], "streak": self.streak[1]}},
                upsert=True,
            )

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

    @checks.has_permissions(PermissionLevel.OWNER)
    @commands.command()
    async def reimbursecookieclicks(self, ctx: commands.Context):
        """
        Reimburses all users for the clicks they spent on cookies.

        There used to be a button that gives them a cookie for 1 click, but it has been removed.
        This command reimburses all users for the clicks they lost.

        Here is the old cookie code: [github](https://github.com/RealCyGuy/modmail-plugins/blob/8803a954e7856aa5c3a30dad060e4abf90ea22af/clickthebutton/views.py#L215).
        """
        async for user in self.db.find({"user": True}):
            if user.get("cookies", 0) > 0:
                self.leaderboard[str(user["id"])] += user["cookies"]
                await ctx.send(
                    f"Reimbursing <@{user['id']}> with {user['cookies']} click(s). Updated clicks: {self.leaderboard[str(user['id'])]}."
                )

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def setwinnerrole(self, ctx, role_id: int):
        """
        Set role for first place. Set to 0 to be none.
        """
        self.winner_role_id = role_id
        await self.db.update_one(
            {"_id": "config"},
            {
                "$set": {
                    "winner_role": self.winner_role_id,
                }
            },
            upsert=True,
        )
        await ctx.send(f"Winner role id set to `{self.winner_role_id}`")


async def setup(bot):
    await bot.add_cog(ClickTheButton(bot))
