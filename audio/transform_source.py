from __future__ import annotations
import re
import logging
from dataclasses import dataclass

import httpx
import wavelink
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)


@dataclass
class TransformSource:
    name:        str
    regex:       str
    replacement: str
    selector:    str
    fmt:         str

    def matches(self, identifier: str) -> bool:
        try:
            return bool(re.fullmatch(self.regex, identifier))
        except re.error:
            return False

    async def resolve(self, identifier: str) -> wavelink.Playable | None:
        try:
            url = re.sub(self.regex, self.replacement, identifier)
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            el = soup.select_one(self.selector)
            if not el:
                log.warning(f"Transform '{self.name}': selector '{self.selector}' found nothing at {url}")
                return None
            value = el.get_text()
            query = self.fmt.format(value)
            results = await wavelink.Playable.search(query)
            return results[0] if results else None
        except Exception as e:
            log.warning(f"Transform '{self.name}' failed: {e}")
            return None


def load_transforms(transforms_dict: dict) -> list[TransformSource]:
    sources: list[TransformSource] = []
    for name, cfg in transforms_dict.items():
        try:
            sources.append(TransformSource(
                name        = name,
                regex       = cfg["regex"],
                replacement = cfg["replacement"],
                selector    = cfg["selector"],
                fmt         = cfg["format"],
            ))
        except Exception as e:
            log.warning(f"Invalid transform '{name}': {e}")
    return sources
