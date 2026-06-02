from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
from utils.format_util import volume_icon
if TYPE_CHECKING:
    from bot import MusicBot

class VolumeCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="volume", aliases=["vol"], help="Sets the volume (0–150), or shows current volume")
    @commands.guild_only()
    @is_dj()
    async def volume(self, ctx: commands.Context, level: int = -1) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        player = ctx.voice_client
        if level == -1:
            await ctx.send(f"{volume_icon(player.volume)} Current volume: **{player.volume}**")
            return
        if not 0 <= level <= 150:
            await ctx.send(f"{self.bot.config.error} Volume must be between 0 and 150.")
            return
        await player.set_volume(level)
        self.bot.settings_manager.get_settings(ctx.guild.id).set_volume(level)
        await ctx.send(f"{volume_icon(level)} Volume set to **{level}**.")

async def setup(bot: "MusicBot") -> None:
    cog = VolumeCog(bot)
    cog.volume.aliases = bot.config.get_aliases("volume") or ["vol"]
    await bot.add_cog(cog)
