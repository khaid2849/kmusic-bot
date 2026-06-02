from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands

from audio.queued_track import QueuedTrack
from audio.request_metadata import RequestMetadata
from commands.dj_command import check_dj_permission
from commands.music_command import music_check
from utils.format_util import filter_text
from utils.time_util import format_time

if TYPE_CHECKING:
    from bot import MusicBot


class PlaylistLoadView(discord.ui.View):
    def __init__(self, bot: "MusicBot", playlist: wavelink.Playlist, loaded_track: wavelink.Playable,
                 add_message: str, handler, metadata: RequestMetadata):
        super().__init__(timeout=30)
        self._bot          = bot
        self._playlist     = playlist
        self._loaded_track = loaded_track
        self._add_message  = add_message
        self._handler      = handler
        self._metadata     = metadata
        self._used         = False

    @discord.ui.button(label="📥 Load Playlist", style=discord.ButtonStyle.primary)
    async def load_playlist(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self._used:
            return
        self._used = True
        count = 0
        for track in self._playlist.tracks:
            if track == self._loaded_track:
                continue
            if self._bot.config.is_too_long(track.length or 0):
                continue
            qt = QueuedTrack(track, self._metadata)
            self._handler.add_track(qt)
            count += 1
        await interaction.response.edit_message(
            content=filter_text(f"{self._add_message}\n{self._bot.config.success} Loaded **{count}** additional tracks!"),
            view=None,
        )

    @discord.ui.button(label="🚫 Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self._used:
            return
        self._used = True
        await interaction.response.edit_message(content=filter_text(self._add_message), view=None)

    async def on_timeout(self) -> None:
        pass


class PlayCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="play", aliases=[], help="Plays the provided song or URL")
    @commands.guild_only()
    async def play(self, ctx: commands.Context, *, query: str = "") -> None:
        self.play.aliases = self.bot.config.get_aliases("play")

        if not await music_check(ctx, be_listening=True):
            return

        # Handle file attachment
        if not query and ctx.message.attachments:
            query = ctx.message.attachments[0].url

        player: wavelink.Player = ctx.voice_client  # type: ignore
        handler = self.bot.player_manager.get_handler(ctx.guild)

        # No args + paused = resume
        if not query:
            if player and player.paused and player.current:
                if await check_dj_permission(ctx):
                    await player.pause(False)
                    await ctx.send(f"{self.bot.config.success} Resumed **{player.current.title}**.")
                else:
                    await ctx.send(f"{self.bot.config.error} Only DJs can unpause the player!")
            else:
                await ctx.send(
                    f"{self.bot.config.warning} Play commands:\n"
                    f"`{ctx.prefix}play <song title>` — plays the first YouTube result\n"
                    f"`{ctx.prefix}play <URL>` — plays a URL, playlist, or stream\n"
                    f"`{ctx.prefix}play playlist <name>` — plays a local playlist"
                )
            return

        # Strip angle brackets
        if query.startswith("<") and query.endswith(">"):
            query = query[1:-1]

        loading_msg = await ctx.send(f"{self.bot.config.loading} Loading... `[{query}]`")

        # Check transforms first
        transformed = await self.bot.player_manager.resolve_transforms(query)
        if transformed:
            await self._add_single(ctx, loading_msg, handler, transformed, None)
            return

        try:
            results = await wavelink.Playable.search(query)
        except Exception as e:
            await loading_msg.edit(content=f"{self.bot.config.error} Error loading: {e}")
            return

        if not results:
            await loading_msg.edit(content=f"{self.bot.config.warning} No results found for `{query}`.")
            return

        if isinstance(results, wavelink.Playlist):
            await self._handle_playlist(ctx, loading_msg, handler, results)
        else:
            await self._add_single(ctx, loading_msg, handler, results[0], None)

    async def _add_single(self, ctx, msg, handler, track: wavelink.Playable,
                          playlist: wavelink.Playlist | None) -> None:
        if self.bot.config.is_too_long(track.length or 0):
            await msg.edit(content=filter_text(
                f"{self.bot.config.warning} This track (**{track.title}**) is longer than the allowed maximum: "
                f"`{format_time(track.length or 0)}` > `{self.bot.config.get_max_time_str()}`"
            ))
            return

        metadata = RequestMetadata.from_user(track.uri or "", ctx.author, query=ctx.kwargs.get("query", ""))
        track._rm = metadata
        qt  = QueuedTrack(track, metadata)
        pos = handler.add_track(qt) + 1
        add_msg = filter_text(
            f"{self.bot.config.success} Added **{track.title}** "
            f"(`{format_time(track.length or 0)}`) "
            + ("to begin playing" if pos == 0 else f"to the queue at position **{pos}**")
        )

        if playlist and len(playlist.tracks) > 1:
            view = PlaylistLoadView(self.bot, playlist, track, add_msg, handler, metadata)
            await msg.edit(
                content=filter_text(
                    f"{add_msg}\n{self.bot.config.warning} This track has a playlist of "
                    f"**{len(playlist.tracks)}** tracks attached. Select 📥 to load playlist."
                ),
                view=view,
            )
        else:
            await msg.edit(content=add_msg)

    async def _handle_playlist(self, ctx, msg, handler, playlist: wavelink.Playlist) -> None:
        if playlist.selected_track is not None:
            await self._add_single(ctx, msg, handler, playlist.selected_track, playlist)
            return

        if len(playlist.tracks) == 0:
            await msg.edit(content=filter_text(
                f"{self.bot.config.warning} The playlist (**{playlist.name}**) could not be loaded or contained 0 entries."
            ))
            return

        metadata = RequestMetadata.from_user("", ctx.author)
        count, skipped = 0, 0
        for track in playlist.tracks:
            if self.bot.config.is_too_long(track.length or 0):
                skipped += 1
                continue
            track._rm = metadata
            handler.add_track(QueuedTrack(track, metadata))
            count += 1

        if count == 0:
            await msg.edit(content=filter_text(
                f"{self.bot.config.warning} All entries in **{playlist.name}** exceeded the max length "
                f"(`{self.bot.config.get_max_time_str()}`)."
            ))
        else:
            text = filter_text(
                f"{self.bot.config.success} Found playlist **{playlist.name}** with `{len(playlist.tracks)}` entries; added to the queue!"
            )
            if skipped:
                text += f"\n{self.bot.config.warning} {skipped} track(s) exceeded max length and were omitted."
            await msg.edit(content=text)

    @commands.command(name="playlist", aliases=["pl"], help="Plays a local playlist")
    @commands.guild_only()
    async def play_playlist(self, ctx: commands.Context, *, name: str = "") -> None:
        if not await music_check(ctx, be_listening=True):
            return
        if not name:
            await ctx.send(f"{self.bot.config.error} Please provide a playlist name.")
            return
        playlist = self.bot.playlist_loader.get_playlist(name)
        if not playlist:
            await ctx.send(f"{self.bot.config.error} I could not find `{name}.txt` in the Playlists folder.")
            return

        handler = self.bot.player_manager.get_handler(ctx.guild)
        msg = await ctx.send(f"{self.bot.config.loading} Loading playlist **{name}**... ({len(playlist.items)} items)")

        metadata = RequestMetadata.from_user("", ctx.author)

        async def on_track(track: wavelink.Playable) -> None:
            track._rm = metadata
            handler.add_track(QueuedTrack(track, metadata))

        async def on_done() -> None:
            lines = [
                f"{self.bot.config.success} Loaded **{len(playlist.tracks)}** tracks!"
                if playlist.tracks else
                f"{self.bot.config.warning} No tracks were loaded!"
            ]
            if playlist.errors:
                lines.append("The following tracks failed to load:")
                for err in playlist.errors:
                    lines.append(f"`[{err.index + 1}]` **{err.item}**: {err.reason}")
            text = "\n".join(lines)
            if len(text) > 2000:
                text = text[:1994] + " (...)"
            await msg.edit(content=filter_text(text))

        await playlist.load_tracks(on_track, on_done, self.bot.config)


async def setup(bot: "MusicBot") -> None:
    cog = PlayCog(bot)
    cog.play.aliases = bot.config.get_aliases("play")
    await bot.add_cog(cog)
