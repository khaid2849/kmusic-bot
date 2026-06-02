from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class ForceskipCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="forceskip", aliases=["modskip"], help="Forcefully skips the current song")
    @commands.guild_only()
    @is_dj()
    async def forceskip(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_playing=True, be_listening=True):
            return
        player = ctx.voice_client
        title  = player.current.title
        await player.stop()
        await ctx.send(f"{self.bot.config.success} Skipped **{title}**.")

async def setup(bot: "MusicBot") -> None:
    cog = ForceskipCog(bot)
    cog.forceskip.aliases = bot.config.get_aliases("forceskip") or ["modskip"]
    await bot.add_cog(cog)
