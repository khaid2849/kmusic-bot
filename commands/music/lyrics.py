from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from commands.music_command import music_check

if TYPE_CHECKING:
    from bot import MusicBot


class LyricsCog(commands.Cog, name="Music"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="lyrics", help="Gets lyrics for the current or specified song")
    @commands.guild_only()
    async def lyrics(self, ctx: commands.Context, *, title: str = "") -> None:
        if not title:
            player = ctx.voice_client
            if player and player.current:
                title = player.current.title or ""
            if not title:
                await ctx.send(f"{self.bot.config.error} Please specify a song title or play something first.")
                return

        msg = await ctx.send(f"{self.bot.config.searching} Looking up lyrics for `{title}`...")
        try:
            import lyricsgenius
            genius = lyricsgenius.Genius(verbose=False, remove_section_headers=True)
            song   = await self.bot.loop.run_in_executor(None, lambda: genius.search_song(title))
        except Exception:
            song = None

        if not song:
            await msg.edit(content=f"{self.bot.config.warning} No lyrics found for `{title}`.")
            return

        lyrics = song.lyrics.strip()
        if len(lyrics) > 4096:
            lyrics = lyrics[:4090] + "\n..."

        embed = discord.Embed(
            title    = song.title,
            description = lyrics,
            color    = ctx.guild.me.color,
        )
        embed.set_author(name=song.artist)
        embed.set_footer(text="Powered by Genius")
        await msg.edit(content=None, embed=embed)


async def setup(bot: "MusicBot") -> None:
    cog = LyricsCog(bot)
    cog.lyrics.aliases = bot.config.get_aliases("lyrics")
    await bot.add_cog(cog)
