import asyncio
import re
from dataclasses import dataclass

import httpx

LRCLIB_SEARCH = "https://lrclib.net/api/search"
USER_AGENT    = "kmusic-bot"

# Bracketed chunks: (Official MV), [Lyrics], 【MV】 ...
_BRACKETS = re.compile(r"[\(\[【]([^\)\]】]*)[\)\]】]")
# Common video-title noise outside of brackets
_NOISE = re.compile(
    r"\b(official\s+(music\s+)?(video|audio|mv|m/v|lyric\s+video|visualizer)"
    r"|lyric\s+video|lyrics?|m/v|mv|music\s+video|audio|visualizer|hd|4k)\b",
    re.IGNORECASE,
)
_FEAT   = re.compile(r"\s+(ft\.?|feat\.?|featuring)\s+.*$", re.IGNORECASE)
_AUTHOR = re.compile(r"(\s*-\s*topic|vevo|official)$", re.IGNORECASE)


@dataclass
class LyricsResult:
    artist: str
    title:  str
    lyrics: str


def _clean(text: str) -> str:
    text = _BRACKETS.sub(" ", text)
    text = _NOISE.sub(" ", text)
    text = _FEAT.sub("", text)
    text = text.replace("|", " ").strip(" \t-–—:'\"‘’“”")
    return re.sub(r"\s+", " ", text).strip(" '\"‘’“”")


def build_queries(title: str, author: str = "") -> list[str]:
    """Builds lyric search queries from a (YouTube-style) track title and uploader, best first."""
    queries: list[str] = []

    def add(q: str) -> None:
        q = re.sub(r"\s+", " ", q).strip()
        if q and q.lower() not in (x.lower() for x in queries):
            queries.append(q)

    parts = re.split(r"\s+[-–—]\s+", title, maxsplit=1)
    if len(parts) == 2:
        artist_part, song = parts[0], _clean(parts[1])
        add(f"{_clean(artist_part)} {song}")
        # "이하이 (LeeHi) - ONLY" -> also try the romanized name in the brackets
        for alt in _BRACKETS.findall(artist_part):
            add(f"{_clean(alt)} {song}")
        add(song)
    else:
        song = _clean(title)
        uploader = _AUTHOR.sub("", author).strip()
        if uploader:
            add(f"{uploader} {song}")
        add(song)
    return queries


async def _search(client: httpx.AsyncClient, query: str) -> list[dict]:
    for attempt in range(2):
        try:
            resp = await client.get(LRCLIB_SEARCH, params={"q": query})
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code < 500:
                return []
        except httpx.HTTPError:
            pass
        if attempt == 0:
            await asyncio.sleep(1.5)  # LRCLIB sometimes answers 503 "busy"
    return []


def _tidy(artist: str, track: str) -> tuple[str, str]:
    """Fixes user-submitted metadata like artist "Ed Sheeran - Shape of You" or track "Rick Astley - Never Gonna..."."""
    if " - " in artist:
        artist = artist.split(" - ", 1)[0]
    if " - " in track and track.lower().startswith(artist.lower()):
        track = track.split(" - ", 1)[1]
    if artist.lower() == track.lower():
        artist = ""
    return artist.strip(), track.strip()


def _matches(r: dict, query: str) -> bool:
    _, track = _tidy(r.get("artistName") or "", r.get("trackName") or "")
    track = _clean(track).lower()
    return bool(track) and track in query.lower()


def _pick(results: list[dict], query: str, duration: float | None) -> dict | None:
    hits = [r for r in results if r.get("plainLyrics")]
    if not hits:
        return None
    # Stable sort keeps LRCLIB's relevance order among equally good entries
    hits.sort(key=lambda r: (not _matches(r, query),
                             abs((r.get("duration") or 0) - duration) if duration else 0))
    return hits[0]


async def find_lyrics(queries: list[str], duration: float | None = None) -> LyricsResult | None:
    """Tries each query against LRCLIB and returns the first match with plain lyrics."""
    async with httpx.AsyncClient(timeout=10, headers={"User-Agent": USER_AGENT}) as client:
        for query in queries:
            hit = _pick(await _search(client, query), query, duration)
            if hit:
                artist, title = _tidy(hit["artistName"], hit["trackName"])
                return LyricsResult(artist, title, hit["plainLyrics"].strip())
    return None


def split_lyrics(lyrics: str, limit: int = 4000) -> list[str]:
    """Splits lyrics into chunks of at most `limit` chars, breaking on lines."""
    chunks, current = [], ""
    for line in lyrics.splitlines():
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) > limit:
            chunks.append(current)
            current = line
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks
