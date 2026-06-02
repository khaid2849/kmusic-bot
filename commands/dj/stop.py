from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class StopCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="stop", aliases=["leave"], help="Stops playback, clears the queue, and disconnects")
    @commands.guild_only()
    @is_dj()
    async def stop(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        if handler:
            handler.stop_and_clear()
        if ctx.voice_client:
            await ctx.voice_client.disconnect(force=True)
        self.bot.player_manager.remove_handler(ctx.guild.id)
        self.bot.nowplaying_handler.clear_last_np_message(ctx.guild)
        await ctx.send(f"{self.bot.config.success} The player has stopped and the queue has been cleared.")

async def setup(bot: "MusicBot") -> None:
    cog = StopCog(bot)
    cog.stop.aliases = bot.config.get_aliases("stop") or ["leave"]
    await bot.add_cog(cog)
