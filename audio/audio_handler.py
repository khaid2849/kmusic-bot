from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import discord
import wavelink

from audio.queued_track import QueuedTrack
from audio.request_metadata import RequestMetadata
from trackqueue.abstract_queue import AbstractQueue
from settings.queue_type import QueueType
from settings.repeat_mode import RepeatMode
from utils.format_util import progress_bar, volume_icon, filter_text
from utils.time_util import format_time

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)

PLAY_EMOJI  = "▶"
PAUSE_EMOJI = "⏸"
STOP_EMOJI  = "⏹"


class AudioHandler:
    def __init__(self, bot: "MusicBot", player: wavelink.Player, guild: discord.Guild):
        self._bot     = bot
        self._player  = player
        self._guild   = guild
        self._votes:  set[int] = set()
        self._default_queue: list[wavelink.Playable] = []

        qt = bot.settings_manager.get_settings(guild.id).queue_type
        self._queue: AbstractQueue[QueuedTrack] = qt.create_instance(None)

    # ── Queue operations ────────────────────────────────────────────────────

    def add_track(self, qt: QueuedTrack) -> int:
        if not self._player.current:
            self._bot.loop.create_task(self._play_now(qt))
            return -1
        return self._queue.add(qt)

    def add_track_to_front(self, qt: QueuedTrack) -> int:
        if not self._player.current:
            self._bot.loop.create_task(self._play_now(qt))
            return -1
        self._queue.add_at(0, qt)
        return 0

    async def _play_now(self, qt: QueuedTrack) -> None:
        start_ms = qt.get_start_timestamp()
        await self._player.play(qt.track, start=start_ms)

    def get_queue(self) -> AbstractQueue[QueuedTrack]:
        return self._queue

    def set_queue_type(self, qt: QueueType) -> None:
        self._queue = qt.create_instance(self._queue)

    def stop_and_clear(self) -> None:
        self._queue.clear()
        self._default_queue.clear()
        self._bot.loop.create_task(self._player.stop())

    @property
    def votes(self) -> set[int]:
        return self._votes

    @property
    def player(self) -> wavelink.Player:
        return self._player

    def is_music_playing(self) -> bool:
        return (
            self._player.connected
            and self._player.current is not None
        )

    def get_request_metadata(self) -> RequestMetadata:
        if not self._player.current:
            return RequestMetadata.EMPTY
        return getattr(self._player.current, "_rm", RequestMetadata.EMPTY)

    # ── Default playlist fallback ────────────────────────────────────────────

    async def play_from_default(self) -> bool:
        if self._default_queue:
            track = self._default_queue.pop(0)
            await self._player.play(track)
            return True

        settings = self._bot.settings_manager.get_settings(self._guild.id)
        if not settings.default_playlist:
            return False

        playlist = self._bot.playlist_loader.get_playlist(settings.default_playlist)
        if not playlist or not playlist.items:
            return False

        async def on_track(track: wavelink.Playable) -> None:
            if not self._player.current:
                await self._player.play(track)
            else:
                self._default_queue.append(track)

        async def on_done() -> None:
            if not playlist.tracks and self._leaves_when_done():
                await self._bot.close_audio_connection(self._guild.id)

        await playlist.load_tracks(on_track, on_done)
        return True

    def _leaves_when_done(self) -> bool:
        # With an idle timeout, IdleHandler decides when to leave instead
        config = self._bot.config
        return not config.stay_in_channel and config.idle_time_until_leave <= 0

    # ── Track event handlers ─────────────────────────────────────────────────

    async def on_track_start(self, track: wavelink.Playable) -> None:
        self._votes.clear()
        self._bot.nowplaying_handler.on_track_update(track)

    async def on_track_end(self, track: wavelink.Playable, reason: str) -> None:
        settings  = self._bot.settings_manager.get_settings(self._guild.id)
        repeat    = settings.repeat_mode
        rm        = getattr(track, "_rm", RequestMetadata.EMPTY)

        if reason == "finished" and repeat != RepeatMode.OFF:
            clone = QueuedTrack(track, rm)
            if repeat == RepeatMode.ALL:
                self._queue.add(clone)
            else:
                self._queue.add_at(0, clone)

        may_start_next = reason in ("finished", "loadFailed")
        if may_start_next:
            if self._queue.is_empty():
                played = await self.play_from_default()
                if not played:
                    self._bot.nowplaying_handler.on_track_update(None)
                    if self._leaves_when_done():
                        await self._bot.close_audio_connection(self._guild.id)
                    if self._player.paused:
                        await self._player.pause(False)
            else:
                next_qt = self._queue.pull()
                start   = next_qt.get_start_timestamp()
                await self._player.play(next_qt.track, start=start)

    # ── Embed builders ───────────────────────────────────────────────────────

    def get_now_playing_embed(self) -> discord.Embed | None:
        if not self.is_music_playing():
            return None
        track    = self._player.current
        rm       = self.get_request_metadata()
        position = self._player.position or 0
        duration = track.length or 0
        progress = (position / duration) if duration > 0 else 0

        embed = discord.Embed(color=self._guild.me.color)
        embed.title = track.title
        if track.uri:
            embed.url = track.uri

        if rm.user:
            embed.set_author(name=rm.user.username, icon_url=rm.user.avatar)

        if hasattr(track, "artwork") and track.artwork and self._bot.config.np_images:
            embed.set_thumbnail(url=track.artwork)
        elif track.uri and "youtube.com/watch?v=" in (track.uri or ""):
            vid_id = track.uri.split("v=")[-1].split("&")[0]
            if self._bot.config.np_images:
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{vid_id}/mqdefault.jpg")

        if track.author:
            embed.set_footer(text=f"Source: {track.author}")

        status = PAUSE_EMOJI if self._player.paused else PLAY_EMOJI
        embed.description = (
            f"{status} {progress_bar(progress)} "
            f"`[{format_time(position)}/{format_time(duration)}]` "
            f"{volume_icon(self._player.volume)}"
        )
        return embed

    def get_no_music_playing_embed(self) -> discord.Embed:
        embed = discord.Embed(title="No music playing", color=self._guild.me.color)
        embed.description = f"{STOP_EMOJI} {progress_bar(-1)} {volume_icon(self._player.volume)}"
        return embed

    @property
    def status_emoji(self) -> str:
        return PAUSE_EMOJI if self._player.paused else PLAY_EMOJI
