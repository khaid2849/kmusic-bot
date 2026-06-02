from __future__ import annotations
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import discord

if TYPE_CHECKING:
    from discord.ext import commands

_YT_TIMESTAMP_RE = re.compile(
    r"youtu(?:\.be|be\..+)/.*\?.*(?!.*list=)t=([\dhms]+)"
)


@dataclass
class UserInfo:
    id:       int
    username: str
    discrim:  str
    avatar:   str


@dataclass
class RequestInfo:
    query:           str
    url:             str
    start_timestamp: int = 0

    def __post_init__(self) -> None:
        if not self.start_timestamp:
            self.start_timestamp = _try_get_timestamp(self.query or self.url)


@dataclass
class RequestMetadata:
    user:         UserInfo | None
    request_info: RequestInfo | None

    EMPTY: "RequestMetadata"  # assigned after class body

    def get_owner(self) -> int:
        return self.user.id if self.user else 0

    @classmethod
    def from_ctx(cls, track_uri: str, ctx: "commands.Context") -> "RequestMetadata":
        u = ctx.author
        user_info = UserInfo(
            id=u.id,
            username=u.name,
            discrim=getattr(u, "discriminator", "0") or "0",
            avatar=str(u.display_avatar.url),
        )
        req_info = RequestInfo(query=ctx.kwargs.get("query", ""), url=track_uri)
        return cls(user=user_info, request_info=req_info)

    @classmethod
    def from_user(cls, track_uri: str, user: discord.Member | discord.User, query: str = "") -> "RequestMetadata":
        user_info = UserInfo(
            id=user.id,
            username=user.name,
            discrim=getattr(user, "discriminator", "0") or "0",
            avatar=str(user.display_avatar.url),
        )
        req_info = RequestInfo(query=query, url=track_uri)
        return cls(user=user_info, request_info=req_info)


RequestMetadata.EMPTY = RequestMetadata(user=None, request_info=None)


def _try_get_timestamp(url: str) -> int:
    if not url:
        return 0
    m = _YT_TIMESTAMP_RE.search(url)
    if not m:
        return 0
    from utils.time_util import parse_unit_time
    return parse_unit_time(m.group(1))
