from __future__ import annotations
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import discord
from discord.ext import tasks

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)


class AloneInVoiceHandler:
    def __init__(self, bot: "MusicBot"):
        self._bot        = bot
        self._alone_since: dict[int, datetime] = {}
        self._threshold  = 0

    def init(self) -> None:
        self._threshold = self._bot.config.alone_time_until_stop
        if self._threshold > 0:
            self._check_loop.start()

    def on_voice_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after:  discord.VoiceState,
    ) -> None:
        if self._threshold <= 0:
            return
        guild = member.guild
        if not self._bot.player_manager.has_handler(guild):
            return

        alone  = self._is_alone(guild)
        in_map = guild.id in self._alone_since

        if not alone and in_map:
            del self._alone_since[guild.id]
        elif alone and not in_map:
            self._alone_since[guild.id] = datetime.now(timezone.utc)

    @tasks.loop(seconds=5)
    async def _check_loop(self) -> None:
        now       = datetime.now(timezone.utc)
        to_remove = []
        for guild_id, since in list(self._alone_since.items()):
            elapsed = (now - since).total_seconds()
            if elapsed < self._threshold:
                continue
            guild = self._bot.get_guild(guild_id)
            if not guild:
                to_remove.append(guild_id)
                continue
            handler = self._bot.player_manager.get_handler(guild)
            if handler:
                handler.stop_and_clear()
            if guild.voice_client:
                await guild.voice_client.disconnect(force=True)
            self._bot.player_manager.remove_handler(guild_id)
            to_remove.append(guild_id)
            log.info(f"Left voice in guild {guild_id} (alone for {elapsed:.0f}s)")

        for gid in to_remove:
            self._alone_since.pop(gid, None)

    @_check_loop.before_loop
    async def _before_loop(self) -> None:
        await self._bot.wait_until_ready()

    @staticmethod
    def _is_alone(guild: discord.Guild) -> bool:
        vc = guild.voice_client
        if not vc or not vc.channel:
            return False
        for member in vc.channel.members:
            if not member.bot and not member.voice.deaf:
                return False
        return True
