from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class ForceremoveCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="forceremove", aliases=["forcedelete", "modremove"], help="Removes all queue entries from a user")
    @commands.guild_only()
    @is_dj()
    async def forceremove(self, ctx: commands.Context, *, user: discord.Member) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        count   = handler.get_queue().remove_all(user.id)
        if count == 0:
            await ctx.send(f"{self.bot.config.warning} **{user.display_name}** had no tracks in the queue.")
        else:
            await ctx.send(f"{self.bot.config.success} Removed **{count}** track(s) queued by **{user.display_name}**.")

async def setup(bot: "MusicBot") -> None:
    cog = ForceremoveCog(bot)
    cog.forceremove.aliases = bot.config.get_aliases("forceremove") or ["forcedelete", "modremove"]
    await bot.add_cog(cog)
