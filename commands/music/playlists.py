from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot import MusicBot


class PlaylistsCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="playlists", aliases=["pls"], help="Shows all available local playlists")
    @commands.guild_only()
    async def playlists(self, ctx: commands.Context) -> None:
        names = self.bot.playlist_loader.get_playlist_names()
        if not names:
            await ctx.send(f"{self.bot.config.warning} There are no playlists in the Playlists folder.")
            return
        lines = "\n".join(f"• `{name}`" for name in sorted(names))
        embed = discord.Embed(
            title="Available Playlists",
            description=lines,
            color=ctx.guild.me.color,
        )
        embed.set_footer(text=f"Use {ctx.prefix}play playlist <name> to play one")
        await ctx.send(embed=embed)


async def setup(bot: "MusicBot") -> None:
    cog = PlaylistsCog(bot)
    cog.playlists.aliases = bot.config.get_aliases("playlists") or ["pls"]
    await bot.add_cog(cog)
