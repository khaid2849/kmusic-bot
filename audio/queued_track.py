from __future__ import annotations

import wavelink

from audio.request_metadata import RequestMetadata
from trackqueue.abstract_queue import Queueable
from utils.time_util import format_time


class QueuedTrack(Queueable):
    def __init__(self, track: wavelink.Playable, metadata: RequestMetadata | None = None):
        self.track    = track
        self.metadata = metadata or RequestMetadata.EMPTY

    def get_identifier(self) -> int:
        return self.metadata.get_owner()

    def get_start_timestamp(self) -> int:
        if self.metadata.request_info:
            return self.metadata.request_info.start_timestamp
        return 0

    def __str__(self) -> str:
        duration = format_time(self.track.length or 0)
        title = self.track.title or "Unknown"
        uri   = self.track.uri  or ""
        owner = self.metadata.get_owner()
        track_str = f"[**{title}**]({uri})" if uri.startswith("http") else f"**{title}**"
        return f"`[{duration}]` {track_str} - <@{owner}>"
