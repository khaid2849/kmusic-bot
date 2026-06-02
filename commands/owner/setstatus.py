from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

_STATUS_MAP = {
    "online":    discord.Status.online,
    "idle":      discord.Status.idle,
    "dnd":       discord.Status.dnd,
    "invisible": discord.Status.invisible,
}

class SetstatusCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setstatus", help="Sets the bot's online status (online/idle/dnd/invisible)")
    @is_owner()
    async def setstatus(self, ctx: commands.Context, *, status: str = "") -> None:
        st = _STATUS_MAP.get(status.lower().strip())
        if st is None:
            await ctx.send(f"{self.bot.config.error} Valid statuses: {', '.join(_STATUS_MAP.keys())}.")
            return
        await self.bot.change_presence(status=st)
        await ctx.send(f"{self.bot.config.success} Status set to `{status.lower()}`.")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(SetstatusCog(bot))
