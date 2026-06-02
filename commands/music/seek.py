from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands

from commands.music_command import music_check
from utils.time_util import parse_time

if TYPE_CHECKING:
    from bot import MusicBot


class SeekCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="seek", help="Seeks to a position in the current track (e.g. 1:30, +30, -1:00)")
    @commands.guild_only()
    async def seek(self, ctx: commands.Context, *, time_str: str = "") -> None:
        if not await music_check(ctx, be_playing=True, be_listening=True):
            return
        if not time_str:
            await ctx.send(f"{self.bot.config.error} Please provide a time (e.g. `1:30`, `+30`, `-1:00`).")
            return

        player = ctx.voice_client
        if not player.current or not player.current.is_seekable:
            await ctx.send(f"{self.bot.config.error} This track is not seekable.")
            return

        seek_time = parse_time(time_str)
        if seek_time is None:
            await ctx.send(f"{self.bot.config.error} Invalid time format. Use `1:30`, `1h30m`, `+30`, or `-1:00`.")
            return

        duration = player.current.length or 0
        if seek_time.relative:
            new_pos = max(0, min(player.position + seek_time.milliseconds, duration))
        else:
            new_pos = max(0, min(seek_time.milliseconds, duration))

        await player.seek(int(new_pos))
        from utils.time_util import format_time
        await ctx.send(f"{self.bot.config.success} Seeked to `{format_time(new_pos)}`.")


async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(SeekCog(bot))
