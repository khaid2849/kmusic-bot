from __future__ import annotations
import asyncio
import logging
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands, tasks

from utils.other_util import get_latest_version, get_current_version, NEW_VERSION_AVAILABLE

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)


class BotListeners(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        log.info(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")

        if not self.bot.guilds:
            log.warning("Bot is not in any guilds!")
            log.warning(f"Invite URL: {discord.utils.oauth_url(self.bot.user.id)}")

        for guild in self.bot.guilds:
            try:
                settings = self.bot.settings_manager.get_settings(guild.id)
                vc = settings.get_voice_channel(guild)
                defpl = settings.default_playlist
                if vc and defpl:
                    player = await vc.connect(cls=wavelink.Player)
                    handler = await self.bot.player_manager.setup_handler(guild)
                    if handler:
                        await handler.play_from_default()
            except Exception as e:
                log.debug(f"Auto-join failed for guild {guild.id}: {e}")

        if self.bot.config.update_alerts:
            self._version_check.start()

        await self.bot.reset_game()

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.guild:
            self.bot.nowplaying_handler.on_message_delete(message.guild, message.id)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after:  discord.VoiceState,
    ) -> None:
        self.bot.alone_in_voice_handler.on_voice_update(member, before, after)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        log.info(f"Joined guild: {guild.name} (ID: {guild.id})")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        guild = payload.player.guild
        handler = self.bot.player_manager.get_handler(guild)
        if handler:
            await handler.on_track_start(payload.track)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        guild = payload.player.guild
        handler = self.bot.player_manager.get_handler(guild)
        if handler:
            await handler.on_track_end(payload.track, payload.reason)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        log.info(f"Lavalink node ready: {payload.node.uri}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CheckFailure):
            return
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{self.bot.config.error} Missing argument: `{error.param.name}`")
            return
        log.error(f"Unhandled command error in '{ctx.command}': {error}", exc_info=error)

    @tasks.loop(hours=24)
    async def _version_check(self) -> None:
        current = get_current_version()
        latest  = await get_latest_version()
        if latest and latest != current:
            try:
                owner = await self.bot.fetch_user(self.bot.config.owner)
                dm    = await owner.create_dm()
                await dm.send(NEW_VERSION_AVAILABLE.format(current, latest))
            except Exception:
                pass

    @_version_check.before_loop
    async def _before_version_check(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(BotListeners(bot))
