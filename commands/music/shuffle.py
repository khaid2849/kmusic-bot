from __future__ import annotations
import random
from typing import TYPE_CHECKING

from discord.ext import commands

from commands.music_command import music_check

if TYPE_CHECKING:
    from bot import MusicBot


class ShuffleCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="shuffle", help="Shuffles your tracks in the queue")
    @commands.guild_only()
    async def shuffle(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        if not handler or handler.get_queue().is_empty():
            await ctx.send(f"{self.bot.config.error} The queue is empty.")
            return

        count = handler.get_queue().shuffle(ctx.author.id)
        if count == 0:
            await ctx.send(f"{self.bot.config.warning} You have no tracks in the queue to shuffle.")
        else:
            await ctx.send(f"{self.bot.config.success} Shuffled your **{count}** track(s) in the queue.")


async def setup(bot: "MusicBot") -> None:
    cog = ShuffleCog(bot)
    cog.shuffle.aliases = bot.config.get_aliases("shuffle")
    await bot.add_cog(cog)
