import discord
from discord.ext import commands

import asyncio

from captcha.image import ImageCaptcha

import string
import random

from core import checks
from core.models import PermissionLevel

class CaptchaVerification(commands.Cog):
    """Add captcha verification to your server!"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

        self.role = dict()
        self.length = int()
        self.captchas = dict()
        self.casesensitive = bool()

        asyncio.create_task(self._set_val())

        self.true = ["t", "true", "yes", "y"]
        self.false = ["f", "false", "no", "n"]

    async def _update_db(self):
        await self.db.find_one_and_update(
            {"_id": "config"},
            {
                "$set": {
                    "roles": self.role,
                    "length": self.length,
                    "case-sensitive": self.casesensitive,
                }
            },
            upsert=True,
        )
        await self.db.find_one_and_update(
            {"_id": "captchas"},
            {"$set": {"current_captchas": self.captchas}},
            upsert=True,
        )

    async def _set_val(self):
        config = await self.db.find_one({"_id": "config"})
        captchas = await self.db.find_one({"_id": "captchas"})

        if config is None:
            await self.db.find_one_and_update(
                {"_id": "config"},
                {"$set": {"roles": dict(), "length": 7, "case-sensitive": False,}},
                upsert=True,
            )
            config = await self.db.find_one({"_id": "config"})

        if captchas is None:
            await self.db.find_one_and_update(
                {"_id": "captchas"}, {"$set": {"current_captchas": dict()}}, upsert=True
            )

            captchas = await self.db.find_one({"_id": "birthdays"})

        self.role = config.get("roles", dict())
        self.length = config.get("length", 7)
        self.casesensitive = config.get("case-sensitive", False)

        self.captchas = captchas["current_captchas"]

    @commands.command()
    async def captcha(self, ctx, code=None):
        if str(ctx.guild.id) in self.role:
            if code is None:
                code = "".join(
                    random.choices(string.ascii_letters + string.digits, k=self.length)
                )
                image = ImageCaptcha()
                image.write(code, "out.png")
                embed = discord.Embed(
                    colour=self.bot.main_color, title="Your embed, good sir (or ma'am)."
                )
                embed.set_footer(text=f"Use `{self.bot.prefix}captcha <code>` to solve it.")
                embed.set_image(url="attachment://out.py")
                await ctx.author.send(embed=embed)
                await ctx.send(
                    f"{ctx.author.mention}, sent you a DM containing the CAPTCHA!"
                )
                self.captchas[str(ctx.author.id)] = code
            elif str(ctx.author.id) in self.captchas:
                if code == self.captchas[str(ctx.author.id)]:
                    solved = True
                elif (
                    not self.casesensitive
                    and code.lower() == self.captchas[str(ctx.author.id)].lower()
                ):
                    solved = True
                else:
                    await ctx.send(
                        embed=discord.Embed(
                            title=f"That is incorrect. Please try again. `{self.bot.prefix}captcha`",
                            description=f"It is {None if self.casesensitive else 'not '}case-sensitive.",
                            colour=self.bot.error_color,
                        )
                    )
                    solved = False
                if solved:
                    await ctx.send("Solved!")
                    try:
                        role = discord.utils.get(ctx.guild.roles, id=int(self.role[str(ctx.guild.id)]))
                        await ctx.author.add_roles(role)
                    except discord.Forbidden:
                        await ctx.send("I don't have the permissions to give you the role.")
                self.captchas.pop(str(ctx.author.id))

            else:
                await ctx.send(
                    embed=discord.Embed(
                        colour=self.bot.error_color,
                        title="You are not doing a captcha.",
                    )
                )
        else:
            await ctx.send(
                embed=discord.Embed(
                    colour=self.bot.error_color, title="No role set for doing captcha."
                )
            )
    
    @checks.has_permissions(PermissionLevel.ADMIN)
    @commands.group(invoke_without_command=True)
    async def captchaconfig(self, ctx):
        """
        Config your captcha!

        To view your settings, use [p]captchaconfig.

        To edit, use [p]captchaconfig <thingyouwanttoedit> <newvalue>
        """
        role = str(self.role.get(str(ctx.guild.id), "No role specified."))

        embed = discord.Embed(colour=self.bot.main_color, description="These are the captcha settings.")
        embed.set_author(name="Current captcha configs:", icon_url=self.bot.user.avatar_url)
        embed.add_field(name="Role", value=f"`{role}`", inline=False)
        embed.add_field(name="Code Length", value=f"`{self.length}`", inline=False)
        embed.add_field(name="Case sensitive", value=f"`{self.casesensitive}`", inline=False)

    @checks.has_permissions(PermissionLevel.ADMIN)
    @captchaconfig.command()
    async def role(self, ctx, role: discord.Role):
        self.role[str(ctx.guild.id)] = role.id
        await self._update_db()
        await ctx.send("Ok.")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @captchaconfig.command()
    async def length(self, ctx, length=7):
        if length > 0 and length < 20:
            self.length = length
            await self._update_db()
            await ctx.send("Ok.")
        else:
            await ctx.send("Too big or too small.")

    @checks.has_permissions(PermissionLevel.ADMIN)
    @captchaconfig.command()
    async def casesensitive(self, ctx, trueorfalse):
        if trueorfalse.lower() in self.true:
            self.casesensitive = True
        elif trueorfalse.lower in self.false:
            self.casesensitive = False
        else:
            await ctx.send("I don't understand.")
            return
        await self._update_db
        await ctx.send(f"Case sensative is now `{self.casesensitive}`")

def setup(bot):
    bot.add_cog(CaptchaVerification(bot))
