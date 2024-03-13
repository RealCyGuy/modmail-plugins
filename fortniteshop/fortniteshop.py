import asyncio
import datetime
from collections import defaultdict

import aiohttp
import discord
from discord.ext import commands, tasks

from core import checks
from core.models import PermissionLevel


def parse_date(date_str: str) -> datetime.datetime:
    return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=datetime.timezone.utc
    )


class FortniteShop(commands.Cog):
    """Receive the Fortnite item shop in a channel daily."""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.command()
    async def shopchannel(self, ctx, channel: discord.TextChannel = None):
        """
        Set a channel to automatically post the Fortnite shop daily.
        """
        self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"channel": channel.id if channel else None}},
            upsert=True,
        )
        if channel:
            await ctx.send(
                f"Shop channel set to {channel.mention}.\n"
                f"Next shop will be sent <t:{int(self.dailyshop.next_iteration.timestamp())}:R>."
            )
        else:
            await ctx.send("Shop channel removed.")

    async def cog_load(self):
        self.dailyshop.start()

    async def cog_unload(self):
        self.dailyshop.cancel()

    @tasks.loop(time=datetime.time())
    async def dailyshop(self):
        config = await self.db.find_one({"_id": "config"})
        if not config:
            return
        channel_id = config.get("channel")
        if not channel_id:
            return
        channel = self.bot.get_channel(channel_id)

        now = datetime.datetime.now(datetime.timezone.utc)
        for attempt in range(20):
            async with aiohttp.ClientSession() as session:
                async with session.get("https://fortnite-api.com/v2/shop") as resp:
                    shop = await resp.json()

            updated = parse_date(shop["data"]["date"])
            if now - updated > datetime.timedelta(hours=12):
                await asyncio.sleep(attempt)
                continue

            cosmetics = defaultdict(list)
            ids = set()
            for entry in shop["data"]["entries"]:
                br_items = entry.get("brItems", [])
                if br_items:
                    for item in br_items:
                        if item["id"] in ids:
                            continue
                        ids.add(item["id"])
                        name = item["name"]
                        name = f"[{name}](https://fnbr.co/{item['type']['value']}/{item['name'].replace(' ', '-').lower()})"
                        if len(item["shopHistory"]) == 1:
                            name = f"__**{name}**__"
                            days = 999999999
                        else:
                            diff = updated - parse_date(item["shopHistory"][-2])
                            days = diff.days
                            if diff > datetime.timedelta(hours=25):
                                if days > 300:
                                    name += f" (**{days}**)"
                                else:
                                    name += f" ({days})"
                        cosmetics[item["type"]["value"].capitalize() + "s"].append(
                            (name, days)
                        )

            embed = discord.Embed(colour=0x2B2D31)
            keys = ["Outfits", "Emotes", "Pickaxes", "Gliders", "Backpacks"]
            for key in keys:
                values = cosmetics.get(key, [])
                pages = 0
                page = []
                length = 0
                for name, _ in sorted(values, key=lambda x: x[1], reverse=True):
                    if len(page) > 0:
                        length += 2
                    length += len(name)
                    if length > 1024:
                        embed.add_field(name=key, value=", ".join(page), inline=False)
                        if pages == 0:
                            key = f"{key} continued"
                        pages += 1
                        length = len(name)
                        page = []
                    page.append(name)
                if page:
                    embed.add_field(name=key, value=", ".join(page), inline=False)
            embed.set_footer(text="Updated")
            embed.timestamp = updated
            await channel.send(embed=embed)
            break


async def setup(bot):
    await bot.add_cog(FortniteShop(bot))
