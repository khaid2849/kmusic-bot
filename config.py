import sys
import tomllib
from pathlib import Path

import discord

from utils.other_util import parse_game, parse_status
from utils.prompt import Prompt

_DEFAULT_CONFIG = """\
token = "BOT_TOKEN_HERE"
owner = 0
prefix = "@mention"
altprefix = "NONE"
game = "DEFAULT"
status = "online"
song_in_status = false
success = "🎶"
warning = "💡"
error = "🚫"
loading = "⌚"
searching = "🔎"
help = "help"
np_images = false
stay_in_channel = false
max_time = 0
max_yt_playlist_pages = 10
skip_ratio = 0.55
alone_time_until_stop = 0
idle_time_until_leave = 0
playlists_folder = "Playlists"
update_alerts = true
log_level = "info"

[aliases]
settings   = ["status"]
nowplaying = ["np", "current"]
playlists  = ["pls"]
queue      = ["list"]
remove     = ["delete"]
search     = ["ytsearch"]
skip       = ["voteskip"]
prefix     = ["setprefix"]
forceremove = ["forcedelete", "modremove"]
forceskip  = ["modskip"]
movetrack  = ["move"]
stop       = ["leave"]
volume     = ["vol"]
skipto     = ["jumpto"]

[transforms]
"""


class BotConfig:
    def __init__(self, config_path: str = "config.toml"):
        self._path = Path(config_path)
        self._prompt = Prompt("MusicBot")
        self._valid = False

        self.token: str = ""
        self.owner: int = 0
        self.prefix: str = "@mention"
        self.altprefix: str | None = None
        self.game: discord.Activity | None = None
        self.status: discord.Status = discord.Status.online
        self.song_in_status: bool = False
        self.success: str = "🎶"
        self.warning: str = "💡"
        self.error: str = "🚫"
        self.loading: str = "⌚"
        self.searching: str = "🔎"
        self.help: str = "help"
        self.np_images: bool = False
        self.stay_in_channel: bool = False
        self.max_time: int = 0
        self.max_yt_playlist_pages: int = 10
        self.skip_ratio: float = 0.55
        self.alone_time_until_stop: int = 0
        self.idle_time_until_leave: int = 0
        self.playlists_folder: str = "Playlists"
        self.update_alerts: bool = True
        self.log_level: str = "info"
        self._aliases: dict = {}
        self._transforms: dict = {}

    def load(self) -> None:
        self._valid = False

        if not self._path.exists():
            self._write_default()

        try:
            with open(self._path, "rb") as f:
                data = tomllib.load(f)
        except Exception as e:
            self._prompt.alert("ERROR", "Config", f"Failed to read config.toml: {e}")
            return

        self.token               = data.get("token", "")
        self.owner               = int(data.get("owner", 0))
        self.prefix              = data.get("prefix", "@mention")
        alt                      = data.get("altprefix", "NONE")
        self.altprefix           = None if alt.upper() == "NONE" else alt
        self.game                = parse_game(data.get("game", "DEFAULT"))
        self.status              = parse_status(data.get("status", "online"))
        self.song_in_status      = bool(data.get("song_in_status", False))
        self.success             = data.get("success", "🎶")
        self.warning             = data.get("warning", "💡")
        self.error               = data.get("error", "🚫")
        self.loading             = data.get("loading", "⌚")
        self.searching           = data.get("searching", "🔎")
        self.help                = data.get("help", "help")
        self.np_images           = bool(data.get("np_images", False))
        self.stay_in_channel     = bool(data.get("stay_in_channel", False))
        self.max_time            = int(data.get("max_time", 0))
        self.max_yt_playlist_pages = int(data.get("max_yt_playlist_pages", 10))
        self.skip_ratio          = float(data.get("skip_ratio", 0.55))
        self.alone_time_until_stop = int(data.get("alone_time_until_stop", 0))
        self.idle_time_until_leave = int(data.get("idle_time_until_leave", 0))
        self.playlists_folder    = data.get("playlists_folder", "Playlists")
        self.update_alerts       = bool(data.get("update_alerts", True))
        self.log_level           = data.get("log_level", "info")
        self._aliases            = data.get("aliases", {})
        self._transforms         = data.get("transforms", {})

        write_back = False

        if not self.token or self.token == "BOT_TOKEN_HERE":
            token = self._prompt.prompt(
                "No bot token found in config.toml.\n"
                "Please provide your bot token: "
            )
            if not token:
                self._prompt.alert("ERROR", "Config", "No token provided. Exiting.")
                return
            self.token = token
            write_back = True

        if self.owner <= 0:
            raw = self._prompt.prompt(
                "No owner ID found in config.toml.\n"
                "Please provide your Discord user ID: "
            )
            try:
                self.owner = int(raw or "0")
            except ValueError:
                self.owner = 0
            if self.owner <= 0:
                self._prompt.alert("ERROR", "Config", "Invalid owner ID. Exiting.")
                return
            write_back = True

        if write_back:
            self._write_back()

        self._valid = True

    @property
    def is_valid(self) -> bool:
        return self._valid

    def is_too_long(self, duration_ms: int) -> bool:
        if self.max_time <= 0:
            return False
        return round(duration_ms / 1000) > self.max_time

    def get_aliases(self, command: str) -> list[str]:
        return list(self._aliases.get(command, []))

    def get_transforms(self) -> dict:
        return dict(self._transforms)

    def get_max_time_str(self) -> str:
        from utils.time_util import format_time
        return format_time(self.max_time * 1000)

    def _write_default(self) -> None:
        self._prompt.alert("INFO", "Config", f"Writing default config to {self._path}")
        self._path.write_text(_DEFAULT_CONFIG, encoding="utf-8")

    def _write_back(self) -> None:
        try:
            text = self._path.read_text(encoding="utf-8")
            text = text.replace("BOT_TOKEN_HERE", self.token)
            text = text.replace("owner = 0", f"owner = {self.owner}")
            self._path.write_text(text, encoding="utf-8")
        except Exception as e:
            self._prompt.alert("WARNING", "Config", f"Failed to write config back: {e}")

    @staticmethod
    def write_default_config(path: str = "config.toml") -> None:
        p = Path(path)
        p.write_text(_DEFAULT_CONFIG, encoding="utf-8")
        print(f"Default config written to {p.absolute()}")
