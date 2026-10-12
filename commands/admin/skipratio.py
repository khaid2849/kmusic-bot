from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.admin_command import is_admin
if TYPE_CHECKING:
    from bot import MusicBot

class SkipratioCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setskip", usage="<percent | NONE>", aliases=["skipratio"], help="Sets the vote skip ratio (e.g. 55 or 0.55)")
    @commands.guild_only()
    @is_admin()
    async def setskip(self, ctx: commands.Context, *, value: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not value or value.lower() == "none":
            settings.set_skip_ratio(-1)
            default_pct = int(self.bot.config.skip_ratio * 100)
            await ctx.send(f"{self.bot.config.success} Skip ratio reset to global default ({default_pct}%).")
            return
        try:
            ratio = float(value.strip().rstrip("%"))
            if ratio > 1:
                ratio /= 100
        except ValueError:
            await ctx.send(f"{self.bot.config.error} Invalid ratio. Use a number like `55` or `0.55`.")
            return
        if not 0.0 <= ratio <= 1.0:
            await ctx.send(f"{self.bot.config.error} Ratio must be between 0 and 100.")
            return
        settings.set_skip_ratio(ratio)
        await ctx.send(f"{self.bot.config.success} Skip ratio set to **{int(ratio * 100)}%**.")

async def setup(bot: "MusicBot") -> None:
    cog = SkipratioCog(bot)
    cog.setskip.aliases = bot.config.get_aliases("skipratio") or ["skipratio"]
    await bot.add_cog(cog)
