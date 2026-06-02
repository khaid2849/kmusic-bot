from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import discord
import wavelink

from audio.audio_handler import AudioHandler
from audio.transform_source import load_transforms

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)


class PlayerManager:
    def __init__(self, bot: "MusicBot"):
        self._bot      = bot
        self._handlers: dict[int, AudioHandler] = {}

    async def init(self) -> None:
        node = wavelink.Node(
            uri      = "http://localhost:2333",
            password = "youshallnotpass",
        )
        await wavelink.Pool.connect(nodes=[node], client=self._bot)
        log.info("Connected to Lavalink node")

        self._transforms = load_transforms(self._bot.config.get_transforms())
        if self._transforms:
            log.info(f"Loaded {len(self._transforms)} URL transform(s)")

    def has_handler(self, guild: discord.Guild) -> bool:
        return guild.id in self._handlers and guild.voice_client is not None

    def get_handler(self, guild: discord.Guild) -> AudioHandler | None:
        return self._handlers.get(guild.id)

    async def setup_handler(self, guild: discord.Guild) -> AudioHandler:
        if guild.id in self._handlers and guild.voice_client:
            return self._handlers[guild.id]

        player: wavelink.Player = guild.voice_client  # type: ignore
        if player is None:
            return None

        volume = self._bot.settings_manager.get_settings(guild.id).volume
        await player.set_volume(volume)

        handler = AudioHandler(self._bot, player, guild)
        self._handlers[guild.id] = handler
        return handler

    def remove_handler(self, guild_id: int) -> None:
        self._handlers.pop(guild_id, None)

    async def resolve_transforms(self, query: str) -> wavelink.Playable | None:
        for transform in self._transforms:
            if transform.matches(query):
                return await transform.resolve(query)
        return None
