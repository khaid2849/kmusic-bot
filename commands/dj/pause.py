from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class PauseCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="pause", help="Pauses or resumes the current song")
    @commands.guild_only()
    @is_dj()
    async def pause(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_playing=True, be_listening=True):
            return
        player = ctx.voice_client
        if player.paused:
            await player.pause(False)
            await ctx.send(f"{self.bot.config.success} Resumed **{player.current.title}**.")
        else:
            await player.pause(True)
            await ctx.send(f"{self.bot.config.success} Paused **{player.current.title}**.")

async def setup(bot: "MusicBot") -> None:
    cog = PauseCog(bot)
    cog.pause.aliases = bot.config.get_aliases("pause")
    await bot.add_cog(cog)
