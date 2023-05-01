from pathlib import Path

from discord.ext import commands
from watchfiles import awatch

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class HotReload(commands.Cog):
    """Hot-reload local plugins for development!"""

    def __init__(self, bot):
        self.bot = bot
        self.plugins = {}

    async def watch_plugin(self, plugin: str):
        async for _ in awatch(Path("plugins") / "@local" / plugin, debounce=2000):
            extension = f"plugins.@local.{plugin}.{plugin}"
            await self.bot.reload_extension(extension)
            logger.info(f"Reloaded {extension}.")

    @checks.has_permissions(PermissionLevel.OWNER)
    @commands.command()
    async def hotreload(self, ctx, plugin: str = None):
        """Start watching a local plugin for hot-reloading."""
        if plugin is None:
            return await ctx.send("Currently watching: " + ", ".join(self.plugins))

        if plugin in self.plugins:
            self.plugins[plugin].cancel()
            del self.plugins[plugin]
            return await ctx.send(f"Stopped watching `@local/{plugin}`.")

        if f"plugins.@local.{plugin}.{plugin}" not in self.bot.extensions:
            return await ctx.send(
                f"Plugin `@local/{plugin}` does not exist/is not loaded."
            )

        task = self.bot.loop.create_task(self.watch_plugin(plugin))
        self.plugins[plugin] = task
        await ctx.send(f"Watching `@local/{plugin}`.")


async def setup(bot):
    await bot.add_cog(HotReload(bot))
