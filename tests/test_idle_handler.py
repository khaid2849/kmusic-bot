import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from audio.idle_handler import IdleHandler


class FakeAudioHandler:
    def __init__(self, playing: bool, paused: bool = False):
        self.playing = playing
        self.player  = SimpleNamespace(paused=paused)
        self.cleared = False

    def is_music_playing(self) -> bool:
        return self.playing

    def stop_and_clear(self) -> None:
        self.cleared = True


class FakeBot:
    def __init__(self, handler: FakeAudioHandler | None):
        self.guild    = SimpleNamespace(id=1, voice_client=object())
        self.guilds   = [self.guild]
        self.handler  = handler
        self.closed   = []
        self.removed  = []
        self.config   = SimpleNamespace(idle_time_until_leave=7200)
        self.player_manager = SimpleNamespace(
            get_handler    = lambda guild: self.handler,
            remove_handler = self.removed.append,
        )

    def get_guild(self, guild_id):
        return self.guild if guild_id == 1 else None

    async def close_audio_connection(self, guild_id):
        self.closed.append(guild_id)
        self.guild.voice_client = None


def make(handler):
    bot  = FakeBot(handler)
    idle = IdleHandler(bot)
    idle._threshold = bot.config.idle_time_until_leave
    return bot, idle


async def tick(idle):
    await idle._check_loop.coro(idle)


async def test_starts_timer_but_stays_before_threshold():
    bot, idle = make(FakeAudioHandler(playing=False))
    await tick(idle)
    assert 1 in idle._idle_since and bot.closed == []


async def test_leaves_after_threshold_when_stopped():
    audio = FakeAudioHandler(playing=False)
    bot, idle = make(audio)
    idle._idle_since[1] = datetime.now(timezone.utc) - timedelta(seconds=7201)
    await tick(idle)
    assert bot.closed == [1] and bot.removed == [1] and audio.cleared
    assert idle._idle_since == {}


async def test_paused_counts_as_idle():
    bot, idle = make(FakeAudioHandler(playing=True, paused=True))
    idle._idle_since[1] = datetime.now(timezone.utc) - timedelta(seconds=7201)
    await tick(idle)
    assert bot.closed == [1]


async def test_playing_resets_timer():
    bot, idle = make(FakeAudioHandler(playing=True))
    idle._idle_since[1] = datetime.now(timezone.utc) - timedelta(seconds=7201)
    await tick(idle)
    assert bot.closed == [] and 1 not in idle._idle_since


async def test_forgets_guild_after_bot_left_voice():
    bot, idle = make(FakeAudioHandler(playing=False))
    await tick(idle)
    bot.guild.voice_client = None
    await tick(idle)
    assert idle._idle_since == {}
