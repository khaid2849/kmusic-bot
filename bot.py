import asyncio
import logging

import discord
from discord.ext import commands

from config import BotConfig

log = logging.getLogger(__name__)


class MusicBot(commands.Bot):
    def __init__(self, config: BotConfig):
        intents = discord.Intents.none()
        intents.guilds          = True
        intents.guild_messages  = True
        intents.guild_reactions = True
        intents.voice_states    = True
        intents.dm_messages     = True
        intents.message_content = True

        prefix = _build_prefix(config)

        super().__init__(
            command_prefix=prefix,
            intents=intents,
            help_command=None,
            activity=config.game,
            status=config.status,
        )

        self.config         = config
        self.settings_manager  = None   # set in setup_hook
        self.player_manager    = None   # set in setup_hook
        self.playlist_loader   = None   # set in setup_hook
        self.nowplaying_handler   = None  # set in setup_hook
        self.alone_in_voice_handler = None  # set in setup_hook
        self.idle_handler           = None  # set in setup_hook
        self._shutting_down = False

    async def setup_hook(self) -> None:
        from settings.settings_manager import SettingsManager
        from audio.player_manager import PlayerManager
        from playlist.playlist_loader import PlaylistLoader
        from audio.nowplaying_handler import NowplayingHandler
        from audio.alone_in_voice_handler import AloneInVoiceHandler
        from audio.idle_handler import IdleHandler

        self.settings_manager        = SettingsManager()
        self.playlist_loader         = PlaylistLoader(self.config)
        self.player_manager          = PlayerManager(self)
        self.nowplaying_handler      = NowplayingHandler(self)
        self.alone_in_voice_handler  = AloneInVoiceHandler(self)
        self.idle_handler            = IdleHandler(self)

        await self.player_manager.init()

        await self._load_cogs()

        self.nowplaying_handler.init()
        self.alone_in_voice_handler.init()
        self.idle_handler.init()

    async def _load_cogs(self) -> None:
        cogs = [
            "listeners",
            "commands.general.about",
            "commands.general.help",
            "commands.general.ping",
            "commands.general.settings_cmd",
            "commands.music.play",
            "commands.music.nowplaying",
            "commands.music.queue",
            "commands.music.skip",
            "commands.music.search",
            "commands.music.scsearch",
            "commands.music.seek",
            "commands.music.shuffle",
            "commands.music.remove",
            "commands.music.playlists",
            "commands.music.lyrics",
            "commands.dj.forceskip",
            "commands.dj.forceremove",
            "commands.dj.pause",
            "commands.dj.stop",
            "commands.dj.volume",
            "commands.dj.repeat",
            "commands.dj.skipto",
            "commands.dj.movetrack",
            "commands.dj.playnext",
            "commands.admin.prefix",
            "commands.admin.setdj",
            "commands.admin.settc",
            "commands.admin.setvc",
            "commands.admin.skipratio",
            "commands.admin.queuetype",
            "commands.owner.autoplaylist",
            "commands.owner.playlist",
            "commands.owner.setavatar",
            "commands.owner.setgame",
            "commands.owner.setname",
            "commands.owner.setstatus",
            "commands.owner.shutdown",
            "commands.owner.debug",
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
            except Exception as e:
                log.error(f"Failed to load cog {cog}: {e}")

    async def close_audio_connection(self, guild_id: int) -> None:
        guild = self.get_guild(guild_id)
        if guild and guild.voice_client:
            await guild.voice_client.disconnect(force=True)

    async def reset_game(self) -> None:
        activity = self.config.game
        await self.change_presence(activity=activity, status=self.config.status)

    async def shutdown(self) -> None:
        if self._shutting_down:
            return
        self._shutting_down = True
        log.info("Shutting down...")
        for guild in self.guilds:
            if guild.voice_client:
                handler = self.player_manager.get_handler(guild)
                if handler:
                    handler.stop_and_clear()
                await guild.voice_client.disconnect(force=True)
        await self.close()


def _build_prefix(config: BotConfig):
    async def get_prefix(bot: MusicBot, message: discord.Message):
        prefixes = []

        if message.guild:
            guild_prefix = bot.settings_manager.get_settings(message.guild.id).prefix
            if guild_prefix:
                prefixes.append(guild_prefix)

        global_prefix = config.prefix
        if global_prefix == "@mention":
            return commands.when_mentioned_or(*prefixes)(bot, message)

        prefixes.append(global_prefix)
        if config.altprefix:
            prefixes.append(config.altprefix)

        return commands.when_mentioned_or(*prefixes)(bot, message)

    return get_prefix
