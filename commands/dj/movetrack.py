from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class MovetracKCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="movetrack", aliases=["move"], help="Moves a track from one position to another")
    @commands.guild_only()
    @is_dj()
    async def movetrack(self, ctx: commands.Context, from_pos: int = 0, to_pos: int = 0) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        q       = handler.get_queue()
        size    = q.size()
        if not (1 <= from_pos <= size and 1 <= to_pos <= size):
            await ctx.send(f"{self.bot.config.error} Positions must be between 1 and {size}.")
            return
        if from_pos == to_pos:
            await ctx.send(f"{self.bot.config.warning} That track is already at position **{to_pos}**.")
            return
        moved = q.move_item(from_pos - 1, to_pos - 1)
        await ctx.send(f"{self.bot.config.success} Moved **{moved.track.title}** to position **{to_pos}**.")

async def setup(bot: "MusicBot") -> None:
    cog = MovetracKCog(bot)
    cog.movetrack.aliases = bot.config.get_aliases("movetrack") or ["move"]
    await bot.add_cog(cog)
