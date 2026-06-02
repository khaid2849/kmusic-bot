from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class SkiptoCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="skipto", aliases=["jumpto"], help="Skips to a position in the queue")
    @commands.guild_only()
    @is_dj()
    async def skipto(self, ctx: commands.Context, position: int = 0) -> None:
        if not await music_check(ctx, be_playing=True, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        q       = handler.get_queue()
        if position < 1 or position > q.size():
            await ctx.send(f"{self.bot.config.error} Position must be between 1 and {q.size()}.")
            return
        q.skip(position - 1)
        await ctx.voice_client.stop()
        await ctx.send(f"{self.bot.config.success} Skipped to track **#{position}**.")

async def setup(bot: "MusicBot") -> None:
    cog = SkiptoCog(bot)
    cog.skipto.aliases = bot.config.get_aliases("skipto") or ["jumpto"]
    await bot.add_cog(cog)
