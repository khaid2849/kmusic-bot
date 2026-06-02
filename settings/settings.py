from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import discord

from settings.repeat_mode import RepeatMode
from settings.queue_type import QueueType

if TYPE_CHECKING:
    from settings.settings_manager import SettingsManager


@dataclass
class Settings:
    _manager: "SettingsManager"
    text_id:  int = 0
    voice_id: int = 0
    role_id:  int = 0
    volume:   int = 100
    default_playlist: str | None = None
    repeat_mode: RepeatMode = field(default=RepeatMode.OFF)
    prefix:      str | None = None
    skip_ratio:  float = -1.0
    queue_type:  QueueType = field(default=QueueType.FAIR)

    # ── Channel / role helpers ──────────────────────────────────────────────

    def get_text_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        return guild.get_channel(self.text_id) if self.text_id else None

    def get_voice_channel(self, guild: discord.Guild) -> discord.VoiceChannel | None:
        return guild.get_channel(self.voice_id) if self.voice_id else None

    def get_role(self, guild: discord.Guild) -> discord.Role | None:
        return guild.get_role(self.role_id) if self.role_id else None

    # ── Setters (auto-persist) ──────────────────────────────────────────────

    def set_text_channel(self, channel: discord.TextChannel | None) -> None:
        self.text_id = channel.id if channel else 0
        self._manager.write_settings()

    def set_voice_channel(self, channel: discord.VoiceChannel | None) -> None:
        self.voice_id = channel.id if channel else 0
        self._manager.write_settings()

    def set_dj_role(self, role: discord.Role | None) -> None:
        self.role_id = role.id if role else 0
        self._manager.write_settings()

    def set_volume(self, volume: int) -> None:
        self.volume = volume
        self._manager.write_settings()

    def set_default_playlist(self, name: str | None) -> None:
        self.default_playlist = name
        self._manager.write_settings()

    def set_repeat_mode(self, mode: RepeatMode) -> None:
        self.repeat_mode = mode
        self._manager.write_settings()

    def set_prefix(self, prefix: str | None) -> None:
        self.prefix = prefix
        self._manager.write_settings()

    def set_skip_ratio(self, ratio: float) -> None:
        self.skip_ratio = ratio
        self._manager.write_settings()

    def set_queue_type(self, qt: QueueType) -> None:
        self.queue_type = qt
        self._manager.write_settings()
