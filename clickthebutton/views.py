import asyncio
import io
import random
from collections import OrderedDict
from datetime import timedelta, timezone
from enum import Enum
from typing import Any, Optional

import brokenaxes
import discord
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib import ticker

from .responses import (
    format_deltatime,
    format_mentions,
    random_cooldown_over,
    random_emoji,
    random_fought_off,
    random_got_a_click,
)
from .silent import send_silent
from .stats import Stats
from .utils import event, find_data_intervals, format_user


class GraphTime(Enum):
    MONTH = 0
    WEEK = 1
    DAY = 2
    HOUR = 3


class BaseView(discord.ui.View):
    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
        item: discord.ui.Item[Any],
        /,
    ):
        raise error


class PersistentView(BaseView):
    def __init__(self, cog):
        super().__init__(timeout=None)
        self.button.custom_id = cog.custom_id
        self.graph.custom_id = cog.custom_id + "3"
        self.cog = cog
        self.add_item(
            discord.ui.Button(
                emoji="\N{books}",
                url="https://github.com/RealCyGuy/modmail-plugins/blob/v4/clickthebutton/clickthebutton.py",
            )
        )

    async def do_stuff(
        self,
        interaction: discord.Interaction,
        user_id,
        points,
        cooldown,
        fought_off: str,
        previous_streak,
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
            mentions = format_mentions(
                clickers, self.cog.clickers, interaction.message.edited_at
            )
            if "{}" in fought_off:
                fought = fought_off.replace("{}", mentions) + " and"
            else:
                fought = f"{fought_off} {mentions} and"
        reaction = random_emoji()

        streak = ""
        if self.cog.streak and self.cog.streak[1] > 1:
            streak = f" **Streak**: {self.cog.streak[1]}"
        elif previous_streak and previous_streak[1] > 1:
            previous_streak_user = self.cog.bot.get_user(previous_streak[0])
            streak = (
                " "
                + (
                    previous_streak_user.name
                    if previous_streak_user
                    else "<@" + previous_streak[0] + ">"
                )
                + f"'s streak of {previous_streak[1]} has ended."
            )
        if not isinstance(interaction.channel, discord.TextChannel):
            return
        message = await send_silent(
            content=f"{reaction} <@{user_id}> ({format_deltatime(self.cog.clickers[interaction.user.id] - interaction.message.edited_at)}){fought} {random_got_a_click()}\n"
            f"You are now at {points} clicks and ranked #{rank} out of {len(self.cog.leaderboard)} players.{streak}",
            channel=interaction.channel,
            silent=cooldown > 5,
        )
        self.cog.delete_after(message, max(5, cooldown - 5))
        try:
            try:
                await message.add_reaction(reaction)
            except discord.HTTPException:
                await message.add_reaction("\N{otter}")
        except:
            pass

        if rank == 1 and self.cog.winner_role_id:
            role = interaction.guild.get_role(self.cog.winner_role_id)
            if role:
                already_has_role = False
                for member in role.members:
                    if member.id == interaction.user.id:
                        already_has_role = True
                    else:
                        await member.remove_roles(
                            role, reason="Not first place in click the button."
                        )
                if not already_has_role:
                    await interaction.user.add_roles(
                        role, reason="First place in click the button!"
                    )

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
        try:
            await interaction.response.defer()
        except discord.HTTPException:
            pass

        points = self.cog.leaderboard.get(user_id, 0) + 1
        self.cog.leaderboard[user_id] = points
        await self.cog.db.update_one(
            {"_id": "data"},
            {"$set": {"leaderboard": self.cog.leaderboard}},
            upsert=True,
        )
        await self.cog.dbGraph.insert_one(
            {
                "timestamp": discord.utils.utcnow(),
                "id": user_id,
                "clicks": points,
            }
        )
        previous_streak = None
        if self.cog.streak and self.cog.streak[0] == interaction.user.id:
            self.cog.streak[1] += 1
        else:
            previous_streak = self.cog.streak.copy()
            self.cog.streak = [interaction.user.id, 1]
        button.style = discord.ButtonStyle.grey
        button.disabled = True
        cooldown = random.choices(
            [(0, 5), (6, 39), (40, 179), (180, 599), (600, 720), (0, 1800)],
            cum_weights=[2, 4, 12, 16, 18, 19],
        )[0]
        cooldown = random.randint(*cooldown)
        await asyncio.sleep(random.randint(1, 4))
        fought = ""
        fought_off_clickers = len(self.cog.clickers) - 1
        fought_off = await random_fought_off(fought_off_clickers)
        if len(self.cog.clickers) >= 2:
            await asyncio.sleep(3)
            if fought_off_clickers == 1:
                fought_off_clickers = f"{fought_off_clickers} person"
            else:
                fought_off_clickers = f"{fought_off_clickers} people"
            if "{}" in fought_off:
                fought = fought_off.replace("{}", fought_off_clickers) + " and"
            else:
                fought = f"{fought_off} {fought_off_clickers} and"
        edit_task = asyncio.create_task(
            interaction.message.edit(
                content=event(
                    f"{format_user(interaction.user)}{fought} is now at {points} clicks.",
                    interaction.message.content,
                ),
                embed=await self.cog.create_leaderboard_embed(cooldown=cooldown),
                view=self,
            )
        )
        asyncio.create_task(
            self.do_stuff(
                interaction, user_id, points, cooldown, fought_off, previous_streak
            )
        )
        if cooldown > 5:
            await asyncio.sleep(cooldown - 4)
            asyncio.create_task(
                interaction.channel.send(
                    random_cooldown_over(
                        Stats(
                            self.cog.streak,
                            self.cog.leaderboard,
                            self.cog.get_sorted_leaderboard(),
                        )
                    ),
                    delete_after=0,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            )
            await asyncio.sleep(4)
        else:
            await asyncio.sleep(cooldown)
        await asyncio.wait_for(edit_task, timeout=5)
        button.style = discord.ButtonStyle.green
        button.disabled = False
        self.cog.clickers = OrderedDict()
        await interaction.message.edit(
            embed=await self.cog.create_leaderboard_embed(),
            view=self,
        )

    @discord.ui.button(
        emoji="\U0001F4C8",
        style=discord.ButtonStyle.gray,
    )
    async def graph(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = GraphViewer(self)
        await view.send(interaction)

    async def create_graph(
        self, graph_time: GraphTime, new_clicks: bool
    ) -> Optional[io.BytesIO]:
        user_clicks = {}

        end_time = discord.utils.utcnow()
        if graph_time == GraphTime.MONTH:
            delta = timedelta(days=30)
        elif graph_time == GraphTime.WEEK:
            delta = timedelta(days=7)
        elif graph_time == GraphTime.DAY:
            delta = timedelta(days=1)
        else:
            delta = timedelta(hours=1)
        start_time = end_time - delta

        async for click in self.cog.dbGraph.find({"timestamp": {"$gt": start_time}}):
            user_id = click["id"]
            if user_id not in user_clicks:
                username = self.cog.bot.get_user(int(user_id))
                if username:
                    username = format_user(username)
                user_clicks[user_id] = {
                    "clicks": [],
                    "timestamps": [],
                    "username": username,
                }
            user_clicks[user_id]["clicks"].append(click["clicks"])
            user_clicks[user_id]["timestamps"].append(
                click["timestamp"].replace(tzinfo=timezone.utc)
            )

        for user_id, data in user_clicks.items():
            data["timestamps"].append(end_time)
            data["clicks"].append(data["clicks"][-1])
            data["timestamps"].insert(0, start_time)
            data["clicks"].insert(0, data["clicks"][0] - 1)
            if new_clicks:
                data["clicks"] = [click - data["clicks"][0] for click in data["clicks"]]

        if len(user_clicks) == 0:
            return None

        sorted_clicks = sorted(
            user_clicks.items(), key=lambda x: x[1]["clicks"][-1], reverse=True
        )
        data_intervals = find_data_intervals(list(user_clicks.values()), not new_clicks)

        plt.style.use("dark_background")
        plt.set_cmap("gist_rainbow")
        plt.rcParams["font.sans-serif"] = [
            "Jetbrains Mono",
            "DejaVu Sans",
        ]

        fig: plt.Figure = plt.figure(figsize=(10, 7))
        bax: brokenaxes.BrokenAxes = brokenaxes.brokenaxes(
            ylims=data_intervals, xlims=((start_time, end_time),), diag_color="white"
        )

        for user_id, data in sorted_clicks:
            bax.step(
                data["timestamps"],
                data["clicks"],
                label=data["username"] if data["username"] else user_id,
                where="post",
            )

        bax.set_title(
            f"{'New b' if new_clicks else 'B'}utton clicks this "
            + graph_time.name.lower()
            + "!",
            pad=25,
            fontsize=16,
        )
        bax.legend(
            loc="center left",
            bbox_to_anchor=(1.0, 1.0),
            frameon=False,
            borderpad=1,
        )
        bax.tick_params(axis="both", colors="white")
        if graph_time in (GraphTime.MONTH, GraphTime.WEEK):
            bax.set_xlabel("Date", color="white", labelpad=30)
        else:
            bax.set_xlabel("Time", color="white", labelpad=30)
        bax.set_ylabel("Clicks", color="white", labelpad=40)
        bax.grid(color="gray")
        bax.grid(color="gray", alpha=0.5, which="minor")

        background_colour = "#2B2D31"
        bax.set_facecolor(background_colour)

        plt.rcParams["timezone"] = "GMT-7"
        for i, ax in enumerate(bax.axs):
            if graph_time == GraphTime.MONTH:
                locator = mdates.DayLocator(interval=3)
                formatter = mdates.DateFormatter("%b %d")
                ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
            elif graph_time == GraphTime.WEEK:
                locator = mdates.DayLocator(interval=1)
                formatter = mdates.DateFormatter("%b %d")
            elif graph_time == GraphTime.DAY:
                locator = mdates.HourLocator(interval=2)
                formatter = mdates.DateFormatter("%I%p")
            else:
                locator = mdates.MinuteLocator(interval=15)
                formatter = mdates.DateFormatter("%I:%M%p")
                ax.xaxis.set_minor_locator(mdates.MinuteLocator(interval=5))
            if i == len(bax.axs) - 1:
                ax.xaxis.set_major_formatter(formatter)
            else:
                ax.xaxis.set_major_formatter(ticker.NullFormatter())

            ax.xaxis.set_major_locator(locator)
            ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

        buffer = io.BytesIO()
        fig.savefig(
            buffer,
            format="png",
            bbox_inches="tight",
            facecolor=background_colour,
            pad_inches=0.3,
        )
        plt.close(fig)
        buffer.seek(0)
        return buffer


class GraphViewer(BaseView):
    def __init__(
        self,
        persistent_view: PersistentView,
        graph_time: GraphTime = GraphTime.WEEK,
        new_clicks: bool = False,
    ):
        super().__init__(timeout=30)
        self.persistent_view = persistent_view
        self.graph_time = graph_time
        self.interaction = None
        self.new_clicks = new_clicks

    @discord.ui.button(
        label="Total clicks", style=discord.ButtonStyle.blurple, disabled=True
    )
    async def total_clicks(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass

    @discord.ui.button(label="Month", style=discord.ButtonStyle.gray)
    async def month(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = GraphViewer(self.persistent_view, GraphTime.MONTH)
        await view.send(interaction)

    @discord.ui.button(label="Week", style=discord.ButtonStyle.gray)
    async def week(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = GraphViewer(self.persistent_view)
        await view.send(interaction)

    @discord.ui.button(label="Day", style=discord.ButtonStyle.gray)
    async def day(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = GraphViewer(self.persistent_view, GraphTime.DAY)
        await view.send(interaction)

    @discord.ui.button(label="Hour", style=discord.ButtonStyle.gray)
    async def hour(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = GraphViewer(self.persistent_view, GraphTime.HOUR)
        await view.send(interaction)

    @discord.ui.button(
        label="New clicks", style=discord.ButtonStyle.blurple, disabled=True
    )
    async def new_clicks(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass

    @discord.ui.button(label="Month", style=discord.ButtonStyle.gray)
    async def new_month(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = GraphViewer(self.persistent_view, GraphTime.MONTH, new_clicks=True)
        await view.send(interaction)

    @discord.ui.button(label="Week", style=discord.ButtonStyle.gray)
    async def new_week(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = GraphViewer(self.persistent_view, new_clicks=True)
        await view.send(interaction)

    @discord.ui.button(label="Day", style=discord.ButtonStyle.gray)
    async def new_day(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = GraphViewer(self.persistent_view, GraphTime.DAY, new_clicks=True)
        await view.send(interaction)

    @discord.ui.button(label="Hour", style=discord.ButtonStyle.gray)
    async def new_hour(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = GraphViewer(self.persistent_view, GraphTime.HOUR, new_clicks=True)
        await view.send(interaction)

    async def send(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        buffer = await self.persistent_view.create_graph(
            self.graph_time, self.new_clicks
        )
        if not buffer:
            return await interaction.followup.send(
                "No data to graph in this time frame.", ephemeral=True
            )
        file = discord.File(buffer, filename="graph.png")
        await interaction.followup.send(file=file, view=self, ephemeral=True)
        self.interaction = interaction

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(view=self)
