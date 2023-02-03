from aiohttp import web
from discord.ext import commands


class WebServer(commands.Cog):
    """
    Runs a simple webserver on port 8080 for stuff like health checks.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_plugins_ready(self):
        async def ping(request):
            return web.Response(text="pong")

        app = web.Application()
        app.add_routes([web.get("/", ping)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, port=8080)
        await site.start()


async def setup(bot):
    await bot.add_cog(WebServer(bot))
