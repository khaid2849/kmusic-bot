from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.admin_command import is_admin
if TYPE_CHECKING:
    from bot import MusicBot

class PrefixCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="prefix", usage="<prefix | NONE>", aliases=["setprefix"], help="Sets the command prefix for this server")
    @commands.guild_only()
    @is_admin()
    async def prefix(self, ctx: commands.Context, *, new_prefix: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not new_prefix or new_prefix.lower() == "none":
            settings.set_prefix(None)
            await ctx.send(f"{self.bot.config.success} Prefix cleared (using global default).")
        else:
            settings.set_prefix(new_prefix)
            await ctx.send(f"{self.bot.config.success} Prefix set to `{new_prefix}`.")

async def setup(bot: "MusicBot") -> None:
    cog = PrefixCog(bot)
    cog.prefix.aliases = bot.config.get_aliases("prefix") or ["setprefix"]
    await bot.add_cog(cog)
