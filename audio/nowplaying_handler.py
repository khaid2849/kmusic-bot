from __future__ import annotations
import logging
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import tasks

if TYPE_CHECKING:
    from bot import MusicBot

log = logging.getLogger(__name__)


class NowplayingHandler:
    def __init__(self, bot: "MusicBot"):
        self._bot   = bot
        self._last_np: dict[int, tuple[int, int]] = {}  # guild_id -> (channel_id, message_id)

    def init(self) -> None:
        if not self._bot.config.np_images:
            self._update_loop.start()

    def set_last_np_message(self, message: discord.Message) -> None:
        if message.guild:
            self._last_np[message.guild.id] = (message.channel.id, message.id)

    def clear_last_np_message(self, guild: discord.Guild) -> None:
        self._last_np.pop(guild.id, None)

    def on_track_update(self, track: wavelink.Playable | None) -> None:
        if not self._bot.config.song_in_status:
            return
        active = sum(1 for g in self._bot.guilds if g.voice_client and g.voice_client.playing)
        if track and active <= 1:
            self._bot.loop.create_task(
                self._bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=track.title or "music",
                ))
            )
        else:
            self._bot.loop.create_task(self._bot.reset_game())

    def on_message_delete(self, guild: discord.Guild, message_id: int) -> None:
        pair = self._last_np.get(guild.id)
        if pair and pair[1] == message_id:
            self._last_np.pop(guild.id, None)

    @tasks.loop(seconds=5)
    async def _update_loop(self) -> None:
        to_remove: list[int] = []
        for guild_id, (channel_id, message_id) in list(self._last_np.items()):
            guild = self._bot.get_guild(guild_id)
            if not guild:
                to_remove.append(guild_id)
                continue
            channel = guild.get_channel(channel_id)
            if not isinstance(channel, discord.TextChannel):
                to_remove.append(guild_id)
                continue
            handler = self._bot.player_manager.get_handler(guild)
            if not handler:
                to_remove.append(guild_id)
                continue
            embed = handler.get_now_playing_embed()
            if embed is None:
                embed = handler.get_no_music_playing_embed()
                to_remove.append(guild_id)
            try:
                msg = channel.get_partial_message(message_id)
                await msg.edit(embed=embed)
            except (discord.NotFound, discord.Forbidden):
                to_remove.append(guild_id)
            except Exception as e:
                log.debug(f"NP update failed for guild {guild_id}: {e}")
                to_remove.append(guild_id)

        for gid in to_remove:
            self._last_np.pop(gid, None)

    @_update_loop.before_loop
    async def _before_loop(self) -> None:
        await self._bot.wait_until_ready()
