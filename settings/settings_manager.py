import json
import logging
from pathlib import Path

from settings.repeat_mode import RepeatMode
from settings.queue_type import QueueType
from settings.settings import Settings

log = logging.getLogger(__name__)
_SETTINGS_FILE = "serversettings.json"


class SettingsManager:
    def __init__(self):
        self._settings: dict[int, Settings] = {}
        self._path = Path(_SETTINGS_FILE)
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            log.info(f"Creating new {_SETTINGS_FILE}")
            self._path.write_text("{}", encoding="utf-8")
            return

        try:
            raw: dict = json.loads(self._path.read_text(encoding="utf-8"))
            for guild_id_str, obj in raw.items():
                guild_id = int(guild_id_str)

                # Legacy: boolean repeat -> enum
                if "repeat_mode" not in obj and obj.get("repeat", False):
                    obj["repeat_mode"] = "ALL"

                repeat = RepeatMode.OFF
                if "repeat_mode" in obj:
                    try:
                        repeat = RepeatMode[obj["repeat_mode"].upper()]
                    except (KeyError, AttributeError):
                        pass

                qt = QueueType.FAIR
                if "queue_type" in obj:
                    try:
                        qt = QueueType.from_str(obj["queue_type"])
                    except ValueError:
                        pass

                self._settings[guild_id] = Settings(
                    _manager         = self,
                    text_id          = int(obj.get("text_channel_id",  0) or 0),
                    voice_id         = int(obj.get("voice_channel_id", 0) or 0),
                    role_id          = int(obj.get("dj_role_id",       0) or 0),
                    volume           = int(obj.get("volume",           100)),
                    default_playlist = obj.get("default_playlist"),
                    repeat_mode      = repeat,
                    prefix           = obj.get("prefix"),
                    skip_ratio       = float(obj.get("skip_ratio", -1.0)),
                    queue_type       = qt,
                )
            log.info(f"Loaded {_SETTINGS_FILE} ({len(self._settings)} guilds)")
        except Exception as e:
            log.warning(f"Failed to load {_SETTINGS_FILE}: {e}")

    def get_settings(self, guild_id: int) -> Settings:
        if guild_id not in self._settings:
            self._settings[guild_id] = self._default(guild_id)
        return self._settings[guild_id]

    def write_settings(self) -> None:
        obj: dict = {}
        for guild_id, s in self._settings.items():
            entry: dict = {}
            if s.text_id:   entry["text_channel_id"]  = str(s.text_id)
            if s.voice_id:  entry["voice_channel_id"] = str(s.voice_id)
            if s.role_id:   entry["dj_role_id"]       = str(s.role_id)
            if s.volume != 100:             entry["volume"]           = s.volume
            if s.default_playlist:          entry["default_playlist"] = s.default_playlist
            if s.repeat_mode != RepeatMode.OFF: entry["repeat_mode"]  = s.repeat_mode.name
            if s.prefix:                    entry["prefix"]           = s.prefix
            if s.skip_ratio != -1.0:        entry["skip_ratio"]       = s.skip_ratio
            if s.queue_type != QueueType.FAIR: entry["queue_type"]    = s.queue_type.key.upper()
            obj[str(guild_id)] = entry
        try:
            self._path.write_text(json.dumps(obj, indent=4), encoding="utf-8")
        except Exception as e:
            log.warning(f"Failed to write {_SETTINGS_FILE}: {e}")

    def _default(self, guild_id: int) -> Settings:
        return Settings(_manager=self)
