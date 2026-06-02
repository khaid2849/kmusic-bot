from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands

from commands.music_command import music_check

if TYPE_CHECKING:
    from bot import MusicBot


class RemoveCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="remove", aliases=["delete"], help="Removes a song from the queue by position")
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, position: int = 0) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        q = handler.get_queue()
        if q.is_empty():
            await ctx.send(f"{self.bot.config.error} The queue is empty.")
            return
        if position < 1 or position > q.size():
            await ctx.send(f"{self.bot.config.error} Position must be between 1 and {q.size()}.")
            return

        qt = q.get(position - 1)
        # Only allow removing own tracks unless DJ
        from commands.dj_command import check_dj_permission
        if qt.get_identifier() != ctx.author.id and not await check_dj_permission(ctx):
            await ctx.send(f"{self.bot.config.error} You can only remove your own tracks!")
            return

        removed = q.remove(position - 1)
        await ctx.send(f"{self.bot.config.success} Removed **{removed.track.title}** from the queue.")


async def setup(bot: "MusicBot") -> None:
    cog = RemoveCog(bot)
    cog.remove.aliases = bot.config.get_aliases("remove") or ["delete"]
    await bot.add_cog(cog)
