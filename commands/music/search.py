from __future__ import annotations
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands

from audio.queued_track import QueuedTrack
from audio.request_metadata import RequestMetadata
from commands.music_command import music_check
from utils.format_util import filter_text
from utils.time_util import format_time

if TYPE_CHECKING:
    from bot import MusicBot


class SearchView(discord.ui.View):
    def __init__(self, bot, tracks, handler, metadata, timeout=30):
        super().__init__(timeout=timeout)
        self._bot = bot
        self._tracks  = tracks
        self._handler = handler
        self._metadata = metadata
        for i, track in enumerate(tracks[:5], 1):
            btn = discord.ui.Button(label=str(i), style=discord.ButtonStyle.primary)
            btn.callback = self._make_callback(i - 1, track)
            self.add_item(btn)
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)
        cancel.callback = self._cancel
        self.add_item(cancel)

    def _make_callback(self, idx, track: wavelink.Playable):
        async def callback(interaction: discord.Interaction):
            if self._bot.config.is_too_long(track.length or 0):
                await interaction.response.edit_message(
                    content=filter_text(f"{self._bot.config.warning} That track is longer than the allowed maximum."),
                    view=None,
                )
                return
            track._rm = self._metadata
            qt  = QueuedTrack(track, self._metadata)
            pos = self._handler.add_track(qt) + 1
            await interaction.response.edit_message(
                content=filter_text(
                    f"{self._bot.config.success} Added **{track.title}** "
                    f"(`{format_time(track.length or 0)}`) "
                    + ("to begin playing" if pos == 0 else f"to the queue at position **{pos}**")
                ),
                view=None,
            )
        return callback

    async def _cancel(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Search cancelled.", view=None)


class SearchCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="search", usage="<query>", aliases=["ytsearch"], help="Searches YouTube and lets you choose a result")
    @commands.guild_only()
    async def search(self, ctx: commands.Context, *, query: str = "") -> None:
        if not await music_check(ctx, be_listening=True):
            return
        if not query:
            await ctx.send(f"{self.bot.config.error} Please provide a search query.")
            return

        msg = await ctx.send(f"{self.bot.config.searching} Searching for `{query}`...")
        try:
            results = await wavelink.Playable.search(f"ytsearch:{query}")
        except Exception as e:
            await msg.edit(content=f"{self.bot.config.error} Search failed: {e}")
            return

        if not results:
            await msg.edit(content=f"{self.bot.config.warning} No results found for `{query}`.")
            return

        tracks = results[:5]
        handler = self.bot.player_manager.get_handler(ctx.guild)
        metadata = RequestMetadata.from_user("", ctx.author, query=query)

        lines = [f"`{i}.` **{t.title}** ({format_time(t.length or 0)})" for i, t in enumerate(tracks, 1)]
        view  = SearchView(self.bot, tracks, handler, metadata)
        await msg.edit(content="\n".join(lines), view=view)


async def setup(bot: "MusicBot") -> None:
    cog = SearchCog(bot)
    cog.search.aliases = bot.config.get_aliases("search") or ["ytsearch"]
    await bot.add_cog(cog)
