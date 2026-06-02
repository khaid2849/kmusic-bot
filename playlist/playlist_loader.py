from __future__ import annotations
import asyncio
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Awaitable, Callable, TYPE_CHECKING

import wavelink

if TYPE_CHECKING:
    from config import BotConfig

log = logging.getLogger(__name__)


@dataclass
class PlaylistLoadError:
    index:  int
    item:   str
    reason: str


class Playlist:
    def __init__(self, name: str, items: list[str], shuffle: bool):
        self.name:    str   = name
        self.items:   list[str] = items
        self.shuffle: bool  = shuffle
        self.tracks:  list[wavelink.Playable] = []
        self.errors:  list[PlaylistLoadError] = []
        self._loaded: bool  = False

    async def load_tracks(
        self,
        on_track: Callable[[wavelink.Playable], Awaitable[None]],
        on_done:  Callable[[], Awaitable[None]],
        config=None,
    ) -> None:
        if self._loaded:
            return
        self._loaded = True

        async def _load_one(index: int, item: str) -> None:
            try:
                results = await wavelink.Playable.search(item)
                if not results:
                    self.errors.append(PlaylistLoadError(index, item, "No matches found."))
                    return
                track = results[0]
                if config and config.is_too_long(track.length or 0):
                    self.errors.append(PlaylistLoadError(index, item, "Track is longer than the allowed maximum."))
                    return
                self.tracks.append(track)
                await on_track(track)
            except Exception as e:
                self.errors.append(PlaylistLoadError(index, item, str(e)))

        await asyncio.gather(*[_load_one(i, item) for i, item in enumerate(self.items)])

        if self.shuffle:
            random.shuffle(self.tracks)

        await on_done()


class PlaylistLoader:
    def __init__(self, config: "BotConfig"):
        self._config = config

    def _folder(self) -> Path:
        return Path(self._config.playlists_folder)

    def folder_exists(self) -> bool:
        return self._folder().exists()

    def create_folder(self) -> None:
        self._folder().mkdir(parents=True, exist_ok=True)

    def get_playlist_names(self) -> list[str]:
        folder = self._folder()
        if not folder.exists():
            self.create_folder()
            return []
        return [f.stem for f in folder.iterdir() if f.suffix == ".txt"]

    def get_playlist(self, name: str) -> Playlist | None:
        if name not in self.get_playlist_names():
            return None
        path = self._folder() / f"{name}.txt"
        try:
            shuffle = False
            items: list[str] = []
            for raw_line in path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("#") or line.startswith("//"):
                    tag = line.replace(" ", "").lower()
                    if tag in ("#shuffle", "//shuffle"):
                        shuffle = True
                else:
                    items.append(line)
            if shuffle:
                random.shuffle(items)
            return Playlist(name, items, shuffle)
        except Exception as e:
            log.warning(f"Failed to read playlist '{name}': {e}")
            return None

    def create_playlist(self, name: str) -> None:
        (self._folder() / f"{name}.txt").touch()

    def delete_playlist(self, name: str) -> None:
        (self._folder() / f"{name}.txt").unlink()

    def append_to_playlist(self, name: str, line: str) -> None:
        path = self._folder() / f"{name}.txt"
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{line.strip()}")

    def write_playlist(self, name: str, content: str) -> None:
        (self._folder() / f"{name}.txt").write_text(content.strip(), encoding="utf-8")
