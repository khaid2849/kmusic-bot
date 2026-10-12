from __future__ import annotations
from typing import TYPE_CHECKING

import wavelink
from discord.ext import commands

from audio.queued_track import QueuedTrack
from audio.request_metadata import RequestMetadata
from commands.music.search import SearchView
from commands.music_command import music_check
from utils.time_util import format_time

if TYPE_CHECKING:
    from bot import MusicBot


class SCSearchCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="scsearch", usage="<query>", help="Searches SoundCloud and lets you choose a result")
    @commands.guild_only()
    async def scsearch(self, ctx: commands.Context, *, query: str = "") -> None:
        if not await music_check(ctx, be_listening=True):
            return
        if not query:
            await ctx.send(f"{self.bot.config.error} Please provide a search query.")
            return

        msg = await ctx.send(f"{self.bot.config.searching} Searching SoundCloud for `{query}`...")
        try:
            results = await wavelink.Playable.search(f"scsearch:{query}")
        except Exception as e:
            await msg.edit(content=f"{self.bot.config.error} Search failed: {e}")
            return

        if not results:
            await msg.edit(content=f"{self.bot.config.warning} No results found on SoundCloud for `{query}`.")
            return

        tracks   = results[:5]
        handler  = self.bot.player_manager.get_handler(ctx.guild)
        metadata = RequestMetadata.from_user("", ctx.author, query=query)
        lines    = [f"`{i}.` **{t.title}** ({format_time(t.length or 0)})" for i, t in enumerate(tracks, 1)]
        view     = SearchView(self.bot, tracks, handler, metadata)
        await msg.edit(content="\n".join(lines), view=view)


async def setup(bot: "MusicBot") -> None:
    cog = SCSearchCog(bot)
    cog.scsearch.aliases = bot.config.get_aliases("scsearch")
    await bot.add_cog(cog)
