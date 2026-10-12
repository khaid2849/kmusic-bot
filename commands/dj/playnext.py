from __future__ import annotations
from typing import TYPE_CHECKING
import wavelink
from discord.ext import commands
from audio.queued_track import QueuedTrack
from audio.request_metadata import RequestMetadata
from commands.dj_command import is_dj
from commands.music_command import music_check
from utils.format_util import filter_text
from utils.time_util import format_time
if TYPE_CHECKING:
    from bot import MusicBot

class PlaynextCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="playnext", usage="<song or URL>", help="Adds a song to the front of the queue")
    @commands.guild_only()
    @is_dj()
    async def playnext(self, ctx: commands.Context, *, query: str = "") -> None:
        if not await music_check(ctx, be_listening=True):
            return
        if not query:
            await ctx.send(f"{self.bot.config.error} Please provide a song title or URL.")
            return
        if query.startswith("<") and query.endswith(">"):
            query = query[1:-1]
        msg = await ctx.send(f"{self.bot.config.loading} Loading... `[{query}]`")
        try:
            results = await wavelink.Playable.search(query)
        except Exception as e:
            await msg.edit(content=f"{self.bot.config.error} Error loading: {e}")
            return
        if not results:
            await msg.edit(content=f"{self.bot.config.warning} No results found for `{query}`.")
            return
        track    = results[0] if not isinstance(results, wavelink.Playlist) else results.tracks[0]
        if self.bot.config.is_too_long(track.length or 0):
            await msg.edit(content=filter_text(f"{self.bot.config.warning} That track exceeds the maximum allowed length."))
            return
        metadata = RequestMetadata.from_user(track.uri or "", ctx.author, query=query)
        track._rm = metadata
        handler  = self.bot.player_manager.get_handler(ctx.guild)
        pos      = handler.add_track_to_front(QueuedTrack(track, metadata)) + 1
        await msg.edit(content=filter_text(
            f"{self.bot.config.success} Added **{track.title}** (`{format_time(track.length or 0)}`) "
            + ("to begin playing" if pos == 0 else "to the front of the queue")
        ))

async def setup(bot: "MusicBot") -> None:
    cog = PlaynextCog(bot)
    cog.playnext.aliases = bot.config.get_aliases("playnext")
    await bot.add_cog(cog)
