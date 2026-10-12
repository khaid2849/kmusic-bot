from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from discord.ext import tasks

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)


class IdleHandler:
    """Leaves voice after the bot has played nothing (stopped or paused) for `idle_time_until_leave` seconds."""

    def __init__(self, bot: "MusicBot"):
        self._bot        = bot
        self._idle_since: dict[int, datetime] = {}
        self._threshold  = 0

    def init(self) -> None:
        self._threshold = self._bot.config.idle_time_until_leave
        if self._threshold > 0:
            self._check_loop.start()

    def _is_idle(self, guild_id: int) -> bool:
        guild   = self._bot.get_guild(guild_id)
        handler = self._bot.player_manager.get_handler(guild) if guild else None
        if not handler:
            return True
        return not handler.is_music_playing() or handler.player.paused

    @tasks.loop(seconds=30)
    async def _check_loop(self) -> None:
        now       = datetime.now(timezone.utc)
        connected = {g.id for g in self._bot.guilds if g.voice_client}

        for guild_id in list(self._idle_since):
            if guild_id not in connected:
                del self._idle_since[guild_id]

        for guild_id in connected:
            if not self._is_idle(guild_id):
                self._idle_since.pop(guild_id, None)
                continue

            since   = self._idle_since.setdefault(guild_id, now)
            elapsed = (now - since).total_seconds()
            if elapsed < self._threshold:
                continue

            guild   = self._bot.get_guild(guild_id)
            handler = self._bot.player_manager.get_handler(guild)
            if handler:
                handler.stop_and_clear()
            await self._bot.close_audio_connection(guild_id)
            self._bot.player_manager.remove_handler(guild_id)
            del self._idle_since[guild_id]
            log.info(f"Left voice in guild {guild_id} (idle for {elapsed:.0f}s)")

    @_check_loop.before_loop
    async def _before_loop(self) -> None:
        await self._bot.wait_until_ready()
