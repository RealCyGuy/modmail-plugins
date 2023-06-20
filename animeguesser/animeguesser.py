import asyncio
import io
import random
from collections import Counter
import difflib
from datetime import datetime
from typing import List, Optional, Set
import xml.etree.ElementTree as ET

import aiohttp
import discord
import ffmpeg
from discord.ext import commands, tasks
import m3u8

from bot import ModmailBot
from core import checks
from core.models import getLogger, PermissionLevel

logger = getLogger(__name__)

query = """
query ($page: Int) {
  Page(perPage: 1, page: $page) {
    media(type: ANIME, popularity_greater: 10000, status_not: NOT_YET_RELEASED, sort: TRENDING_DESC, isAdult: false, genre_not_in: ["Ecchi"]) {
      title {
        romaji
        english
        native
        userPreferred
      }
      synonyms
      id
      coverImage {
        extraLarge
        color
      }
      siteUrl
      startDate {
        year
        month
        day
      }
      format
    }
  }
}
"""
anilist_api = "https://graphql.anilist.co"
enime_api = "https://api.enime.moe"
# https://github.com/Enime-Project/enime.moe/blob/master/components/player/index.tsx
nade_cdn = "https://cdn.nade.me/generate"
formats = {
    "TV": "TV series",
    "TV_SHORT": "TV short",
    "MOVIE": "Movie",
    "SPECIAL": "Special",
    "OVA": "Original video animation",
    "ONA": "Original net animation",
    "MUSIC": "Music video",
}
embed_colour = 0x2B2D31
anidb_api = "http://api.anidb.net:9001/httpapi?client=hello&clientver=1&protover=1&request=anime&aid="


def simplified_titles(title: str) -> Set[str]:
    title = title.lower()
    titles = {title}
    if len(title) > 10:
        titles.add(title.split("/")[0])
        titles.add(title.split(":")[0])
        titles.add(title.split("-")[0])
    for extra_word in [
        "movie",
        "ova",
        "series",
        "special",
        "ona",
        "season",
        "tv",
        "film",
    ]:
        titles.add(title.replace(extra_word, ""))
    clean_titles = set()
    for title in titles:
        clean_titles.add(title.strip().replace("  ", " "))
    return clean_titles


class AnimeGuesser(commands.Cog):
    """
    An anime guessing game plugin featuring automatically extracted random frames from anime.
    Inspired by RinBot and utilizing AniList and Enime APIs.
    """

    def __init__(self, bot: ModmailBot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

        self.active_channels: Set[int] = set()

        self.add_anime_loop.start()

    async def cog_load(self):
        await self.db.create_index("created_at", expireAfterSeconds=604800)

    def cog_unload(self):
        self.add_anime_loop.cancel()

    @checks.has_permissions(PermissionLevel.REGULAR)
    @commands.command(aliases=["ag"])
    async def animeguesser(self, ctx: commands.Context):
        """Start a round of anime guesser."""
        combined_id = int(f"{ctx.guild.id}{ctx.channel.id}")
        if combined_id in self.active_channels:
            return await ctx.send("There is already a round active in this channel.")

        round_data = await self.db.find_one_and_delete({})
        if not round_data:
            return await ctx.send(
                f"No round data. If this persists, ffmpeg might not be installed. Run `{self.bot.prefix}ffmpeg` for more info."
            )

        self.active_channels.add(combined_id)

        embed = discord.Embed(
            colour=embed_colour, description="Round starting in 5 seconds..."
        )
        await ctx.send(embed=embed)
        await asyncio.sleep(5)

        answers = set()
        for answer in round_data["answers"]:
            answers.update(simplified_titles(answer))

        def check(m: discord.Message) -> bool:
            if m.channel != ctx.channel or m.author.bot:
                return False
            for answer in answers:
                seq = difflib.SequenceMatcher(None, m.content.lower(), answer)
                if seq.ratio() > 0.8:
                    return True
            return False

        async def wait_for_answer() -> discord.Message:
            try:
                msg = await self.bot.wait_for("message", check=check)
                return msg
            except asyncio.CancelledError:
                raise

        wait_task = asyncio.create_task(wait_for_answer())
        hint_loop = asyncio.create_task(self.hint_loop(ctx, round_data, wait_task))

        winner: Optional[discord.Message] = None
        try:
            winner = await wait_task
            content = f"{winner.author.mention} guessed the anime correctly!"
        except asyncio.CancelledError:
            content = "No one guessed the anime correctly!"
        hint_loop.cancel()

        colour = (
            int(round_data["colour"][1:], 16) if round_data["colour"] else embed_colour
        )
        embed = discord.Embed(
            colour=colour,
            description=f"{formats.get(round_data['format'], round_data['format'])} released on <t:{round_data['timestamp']}:D>.",
        )
        embed.set_image(url=round_data["cover_image"])
        embed.set_author(name=round_data["title"], url=round_data["url"])
        embed.add_field(name="Answers", value="\n".join(round_data["answers"]))
        send = winner.reply if winner else ctx.send
        await send(
            content=content,
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )
        self.active_channels.remove(combined_id)

    @animeguesser.error
    async def animeguesser_error(self, ctx: commands.Context, error: Exception):
        combined_id = int(f"{ctx.guild.id}{ctx.channel.id}")
        if combined_id in self.active_channels:
            self.active_channels.remove(combined_id)

    async def hint_loop(
        self,
        ctx: commands.Context,
        round_data: dict,
        wait: asyncio.Task,
    ):
        hint = 0
        random.shuffle(round_data["images"])

        hidden_title = ""
        hidden_characters = []
        for i, character in enumerate(round_data["title"]):
            if character == " ":
                hidden_title += " "
            else:
                hidden_title += "_"
                hidden_characters.append(i)
        title_length = len(hidden_characters)

        async def reveal_characters(number: int) -> None:
            nonlocal hidden_title
            nonlocal hidden_characters
            for _ in range(number):
                index = random.choice(hidden_characters)
                hidden_characters.remove(index)
                hidden_title = list(hidden_title)
                hidden_title[index] = round_data["title"][index]
                hidden_title = "".join(hidden_title)
            embed = discord.Embed(colour=embed_colour, description=f"`{hidden_title}`")
            await ctx.send(embed=embed)
            await asyncio.sleep(2)

        for image in round_data["images"]:
            if len(image) == 0:
                continue
            hint += 1
            embed = discord.Embed(colour=embed_colour)
            embed.set_author(name=f"Hint {hint}")
            embed.set_image(url="attachment://image.png")
            await ctx.send(
                embed=embed, file=discord.File(io.BytesIO(image), filename="image.png")
            )
            await asyncio.sleep(random.randint(0, 5))

            if hint == 7:
                await reveal_characters(int(title_length / 18))
            elif hint == 10:
                if title_length >= 11:
                    await reveal_characters(int(title_length / 11))
            elif hint == 13:
                await reveal_characters(max(int(title_length / 9), 1))
            elif hint == 16:
                if title_length >= 7:
                    await reveal_characters(int(title_length / 7))
            elif hint == 19:
                await reveal_characters(max(int(title_length / 4), 1))

        embed = discord.Embed(colour=embed_colour, description="5 seconds left!")
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        wait.cancel()

    @tasks.loop(minutes=2)
    async def add_anime_loop(self):
        try:
            while await self.db.count_documents({}) < 10:
                await self.add_anime()

            if await self.db.count_documents({}) < 100:
                await self.add_anime()
        except Exception as e:
            logger.exception("add_anime_loop exception! waiting 1 minute before resuming loop")
            await asyncio.sleep(60)

    async def add_anime(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                anilist_api,
                json={"query": query, "variables": {"page": random.randint(1, 1000)}},
            ) as resp:
                anilist_data = (await resp.json())["data"]["Page"]["media"][0]
                anilist_id = anilist_data["id"]
                answers: List[str] = anilist_data["synonyms"]
                for title in anilist_data["title"].values():
                    if title not in answers and title is not None:
                        answers.append(title)
                cover_image = anilist_data["coverImage"]["extraLarge"]
                colour = anilist_data["coverImage"]["color"]
                title = anilist_data["title"]["userPreferred"]
                anilist_url = anilist_data["siteUrl"]
                start_date = int(
                    datetime(
                        anilist_data["startDate"]["year"],
                        anilist_data["startDate"]["month"],
                        anilist_data["startDate"]["day"],
                    ).timestamp()
                )
                anime_format = anilist_data["format"]
            async with session.get(
                enime_api + "/mapping/anilist/" + str(anilist_id)
            ) as resp:
                if not resp.ok:
                    return
                enime_data = await resp.json()
                if len(enime_data["episodes"]) == 0:
                    return
                episodes = Counter()
                for episode in random.choices(enime_data["episodes"], k=20):
                    episodes[episode["sources"][0]["id"]] += 1
                anidb_id = enime_data["mappings"].get("anidb")
            if anidb_id:
                async with session.get(anidb_api + str(anidb_id)) as resp:
                    if resp.ok:
                        anidb_data = await resp.text()
                        tree = ET.fromstring(anidb_data)
                        for answer in tree.find("titles").findall("title"):
                            if answer.text not in answers:
                                answers.append(answer.text)
                    else:
                        logger.warning("AniDB API returned a non-200 status code!")
            images: List[bytes] = []
            for episode, count in episodes.items():
                async with session.get(enime_api + "/source/" + episode) as resp:
                    episode_data = await resp.json()
                    url = episode_data["url"]
                async with session.get(nade_cdn, params={"url": url}) as resp:
                    m3u8_url = await resp.text()
                async with session.get(m3u8_url) as resp:
                    m3u8_data = await resp.text()
                    variant_m3u8 = m3u8.loads(m3u8_data)
                    if len(variant_m3u8.playlists) == 0:
                        logger.warning(
                            f"{m3u8_url} has 0 playlists! Anilist ID: {anilist_id} Skipping..."
                        )
                        return
                    lowest_bandwidth = 0
                    lowest_bandwidth_playlist = None
                    for playlist in variant_m3u8.playlists:
                        playlist: m3u8.Playlist = playlist
                        if (
                            lowest_bandwidth == 0
                            or playlist.stream_info.bandwidth < lowest_bandwidth
                        ):
                            lowest_bandwidth = playlist.stream_info.bandwidth
                            lowest_bandwidth_playlist = playlist.absolute_uri
                async with session.get(lowest_bandwidth_playlist) as resp:
                    m3u8_obj = m3u8.loads(await resp.text())
                    for segment in random.choices(m3u8_obj.segments, k=count):
                        async with session.get(segment.absolute_uri) as resp_2:
                            input_stream = await resp_2.read()
                            random_frame_time = random.uniform(0, segment.duration)
                            random_frame_time = max(0.0, random_frame_time - 0.5)
                            result, _ = (
                                ffmpeg.input("pipe:")
                                .output(
                                    "pipe:",
                                    ss=random_frame_time,
                                    vframes=1,
                                    format="image2",
                                )
                                .run(
                                    input=input_stream,
                                    capture_stdout=True,
                                    capture_stderr=True,
                                )
                            )
                            images.append(result)
            await self.db.insert_one(
                {
                    "answers": answers,
                    "images": images,
                    "cover_image": cover_image,
                    "colour": colour,
                    "title": title,
                    "url": anilist_url,
                    "timestamp": start_date,
                    "format": anime_format,
                    "created_at": datetime.utcnow(),
                }
            )

    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True)
    async def ffmpeg(self, ctx: commands.Context):
        """Instructions on how to install FFmpeg."""
        embed = discord.Embed(
            colour=embed_colour,
            description="This plugin requires [FFmpeg](https://en.wikipedia.org/wiki/FFmpeg) to be installed and in path for download anime images!\n\n"
            "To install FFmpeg, you can download it from [their website](https://ffmpeg.org/download.html).\n"
            f"Or you can try `{self.bot.prefix}ffmpeg apt-get` to try installing with apt-get.",
        )
        await ctx.send(embed=embed)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @ffmpeg.command(name="apt-get")
    async def ffmpeg_apt_get(self, ctx: commands.Context):
        """Install FFmpeg with apt-get."""
        proc = await asyncio.create_subprocess_shell(
            "apt-get update",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate()

        proc2 = await asyncio.create_subprocess_shell(
            "apt-get install ffmpeg -y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout2, stderr2 = await proc2.communicate()

        embed = discord.Embed(
            colour=embed_colour,
            description="View the [source code](https://github.com/RealCyGuy/modmail-plugins/blob/v4/animeguesser/animeguesser.py) to debug this more.",
        )
        embed.set_author(name="FFmpeg apt-get installation output")
        embed.add_field(
            name="apt-get update",
            value=f"Output:\n```\u200b{stdout.decode()}```Errors:\n```\u200b{stderr.decode()}```",
        )
        embed.add_field(
            name="apt-get install ffmpeg",
            value=f"Output:\n```\u200b{stdout2.decode()}```Errors:\n```\u200b{stderr2.decode()}```",
        )
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AnimeGuesser(bot))
