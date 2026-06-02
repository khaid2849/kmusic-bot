from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands

from commands.music_command import music_check

if TYPE_CHECKING:
    from bot import MusicBot


class NowplayingCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="nowplaying", aliases=["np", "current"], help="Shows the currently playing song")
    @commands.guild_only()
    async def nowplaying(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_playing=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        embed = handler.get_now_playing_embed()
        if not embed:
            await ctx.send(f"{self.bot.config.success} **Now Playing...**", embed=handler.get_no_music_playing_embed())
            return
        msg = await ctx.send(
            content=f"{self.bot.config.success} **Now Playing in {ctx.guild.me.voice.channel.mention}...**",
            embed=embed,
        )
        self.bot.nowplaying_handler.set_last_np_message(msg)


async def setup(bot: "MusicBot") -> None:
    cog = NowplayingCog(bot)
    cog.nowplaying.aliases = bot.config.get_aliases("nowplaying") or ["np", "current"]
    await bot.add_cog(cog)
