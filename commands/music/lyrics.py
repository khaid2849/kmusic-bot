from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from utils.lyrics_util import build_queries, find_lyrics, split_lyrics

if TYPE_CHECKING:
    from bot import MusicBot

MAX_PAGES = 3


class LyricsCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="lyrics", usage="[song]",
                      help="Shows lyrics for the current song, or for the song you name")
    @commands.guild_only()
    async def lyrics(self, ctx: commands.Context, *, title: str = "") -> None:
        duration = None
        if title:
            queries = [title]
        else:
            player = ctx.voice_client
            track  = player.current if player else None
            if not track:
                await ctx.send(f"{self.bot.config.error} Nothing is playing. Use `lyrics <song name>` to search for a song.")
                return
            title    = track.title
            queries  = build_queries(track.title, track.author or "")
            duration = track.length / 1000 if track.length else None

        msg = await ctx.send(f"{self.bot.config.searching} Looking up lyrics for `{title}`...")
        result = await find_lyrics(queries, duration)
        if not result:
            await msg.edit(content=f"{self.bot.config.warning} No lyrics found for `{title}`. "
                                   f"Try `lyrics <artist> <song>`.")
            return

        pages = split_lyrics(result.lyrics)
        if len(pages) > MAX_PAGES:
            pages = pages[:MAX_PAGES]
            pages[-1] += "\n\n... (lyrics truncated)"

        color = ctx.guild.me.color
        for i, page in enumerate(pages):
            embed = discord.Embed(description=page, color=color)
            if i == 0:
                embed.title = result.title
                if result.artist:
                    embed.set_author(name=result.artist)
            if i == len(pages) - 1:
                embed.set_footer(text="Lyrics from LRCLIB")
            if i == 0:
                await msg.edit(content=None, embed=embed)
            else:
                await ctx.send(embed=embed)


async def setup(bot: "MusicBot") -> None:
    cog = LyricsCog(bot)
    cog.lyrics.aliases = bot.config.get_aliases("lyrics")
    await bot.add_cog(cog)
