import io
import typing
from datetime import datetime, timedelta

import discord
import numpy as np
import pandas as pd
import seaborn as sns
from discord.ext import commands
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.dates import AutoDateLocator
from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collation import Collation, CollationStrength
from pymongo.errors import InvalidName, ConfigurationError
from scipy import stats

from core import checks
from core.models import PermissionLevel
from core.time import human_timedelta


class MarketGraph(commands.Cog):
    """
    Commands that are only useful with a specific MongoDB database schema:
    ```json
    {
        "date": date
        "item": {
            "name": str,
            "amount": int
        },
        "price": {
            "name": str,
            "amount": int
        },
        "rate": float
    }
    ```
    """

    def __init__(self, bot):
        self.bot = bot
        self.plugin_db = bot.plugin_db.get_partition(self)
        self._db: typing.Optional[AgnosticCollection] = None

    async def db(self, ctx: commands.Context) -> typing.Optional[AgnosticCollection]:
        if self._db:
            return self._db
        try:
            config = await self.plugin_db.find_one(
                {"_id": "config"},
            )
            uri = config["uri"]
            database = config["database"]
            collection = config["collection"]
            self._db = AsyncIOMotorClient(uri)[database][collection]
        except (TypeError, KeyError, InvalidName, ConfigurationError):
            await ctx.send(
                "Your mongo database details have been set incorrectly. Run `?setmarketgraph`."
            )
            return
        else:
            return self._db

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMIN)
    async def setmarketgraph(self, ctx, uri: str, database: str, collection: str):
        """
        Set the mongo uri, database name, and collection name of the database.
        """
        await self.plugin_db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"uri": uri, "database": database, "collection": collection}},
            upsert=True,
        )
        self._db = None
        await ctx.send("Set market graph stuff.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def graph(self, ctx, days: typing.Optional[float] = 14, *, price_item: str):
        """
        Graph the price/item rate.
        """
        split = price_item.lower().split("/")
        if len(split) != 2:
            return await ctx.send("Use a `/` to separate the price and item.")
        price = split[0].strip()
        item = split[1].strip()
        db = await self.db(ctx)
        if not db:
            return
        mpl.rcParams.update(mpl.rcParamsDefault)
        sns.set_style("darkgrid")
        sns.set_palette("deep")
        query = {"price.name": price, "item.name": item}
        title = f"{price}/{item} rate"
        if days > 0:
            date = datetime.utcnow() - timedelta(days=days)
            query["date"] = {"$gte": date}
            title += f" since {human_timedelta(date)}"
        data = pd.DataFrame(
            await db.find(
                query,
                collation=Collation("en_US", strength=CollationStrength.SECONDARY),
            ).to_list(length=None)
        )
        if len(data) == 0:
            await ctx.reply("No data found.")
            return
        sub = data.loc[:, "rate"]
        data.loc[:, "rate"] = sub.where(
            np.logical_and(
                sub < sub.quantile(0.99),
                sub > sub.quantile(0.01),
            ),
            np.nan,
        )
        data.dropna(subset="rate", inplace=True)
        means = data.resample("D", on="date")["rate"].mean().to_frame()
        x = "date"
        y = "rate"
        g = sns.JointGrid(data=data, x=x, y=y, space=0.1)
        g.fig.subplots_adjust(top=0.947)
        g.fig.suptitle(title, x=0.07, y=0.97, ha="left", fontsize=20)
        g.fig.set_figwidth(20)
        g.fig.set_figheight(14)
        values = np.vstack([data["date"].values.astype("float64"), data["rate"]])
        kernel = stats.gaussian_kde(values)(values)
        g.plot_joint(sns.kdeplot, fill=True, alpha=0.5)
        g.plot_joint(sns.scatterplot, s=70, c=kernel, cmap="magma", edgecolors=(1, 1, 1, 0.6))
        sns.lineplot(means, x=x, y=y, ax=g.ax_joint, lw=3, alpha=0.7)
        g.plot_marginals(sns.histplot, kde=True)
        g.ax_joint.xaxis.set_major_locator(
            locator=AutoDateLocator(maxticks=70, interval_multiples=False)
        )
        for label in g.ax_joint.get_xticklabels():
            label.set_rotation(90)
        buffer = io.BytesIO()
        g.savefig(
            buffer,
            format="png",
        )
        buffer.seek(0)
        plt.close(g.figure)
        file = discord.File(buffer, filename="graph.png")
        await ctx.send(file=file)


async def setup(bot):
    await bot.add_cog(MarketGraph(bot))
