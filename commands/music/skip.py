from __future__ import annotations
import math
from typing import TYPE_CHECKING

from discord.ext import commands

from commands.dj_command import check_dj_permission
from commands.music_command import music_check

if TYPE_CHECKING:
    from bot import MusicBot


class SkipCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="skip", aliases=["voteskip"], help="Votes to skip the current song")
    @commands.guild_only()
    async def skip(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_playing=True, be_listening=True):
            return

        player  = ctx.voice_client
        handler = self.bot.player_manager.get_handler(ctx.guild)
        track   = player.current

        if await check_dj_permission(ctx):
            await player.stop()
            await ctx.send(f"{self.bot.config.success} Skipped **{track.title}**.")
            return

        handler.votes.add(ctx.author.id)

        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        ratio    = settings.skip_ratio if settings.skip_ratio != -1 else self.bot.config.skip_ratio
        listeners = [
            m for m in player.channel.members
            if not m.bot and not (m.voice and m.voice.deaf)
        ]
        needed = math.ceil(len(listeners) * ratio)
        current_votes = len(handler.votes)

        if current_votes >= needed:
            await player.stop()
            await ctx.send(f"{self.bot.config.success} Skipped **{track.title}**.")
        else:
            await ctx.send(
                f"{self.bot.config.success} Skip vote added. **{current_votes}/{needed}** votes needed to skip."
            )


async def setup(bot: "MusicBot") -> None:
    cog = SkipCog(bot)
    cog.skip.aliases = bot.config.get_aliases("skip") or ["voteskip"]
    await bot.add_cog(cog)
