from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
if TYPE_CHECKING:
    from bot import MusicBot

class PingCog(commands.Cog, name="General"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="ping", help="Shows the bot's latency")
    async def ping(self, ctx: commands.Context) -> None:
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: **{latency_ms}ms**")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(PingCog(bot))
