from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

class ShutdownCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="shutdown", help="Gracefully shuts down the bot")
    @is_owner()
    async def shutdown(self, ctx: commands.Context) -> None:
        await ctx.send(f"{self.bot.config.success} Shutting down...")
        await self.bot.shutdown()

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(ShutdownCog(bot))
