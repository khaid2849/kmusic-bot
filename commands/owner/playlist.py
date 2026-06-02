from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

class PlaylistCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.group(name="playlist", aliases=["pl"], invoke_without_command=True, help="Manage local playlists")
    @is_owner()
    async def playlist(self, ctx: commands.Context) -> None:
        await ctx.send(
            f"{self.bot.config.warning} Playlist subcommands:\n"
            f"`{ctx.prefix}playlist make <name>` — create a new playlist\n"
            f"`{ctx.prefix}playlist delete <name>` — delete a playlist\n"
            f"`{ctx.prefix}playlist append <name> <URL>` — append a URL to a playlist\n"
            f"`{ctx.prefix}playlist write <name> <content>` — overwrite a playlist\n"
        )

    @playlist.command(name="make", help="Creates a new empty playlist")
    async def playlist_make(self, ctx: commands.Context, *, name: str = "") -> None:
        if not name:
            await ctx.send(f"{self.bot.config.error} Please provide a playlist name.")
            return
        name = name.replace(" ", "_")
        if name in self.bot.playlist_loader.get_playlist_names():
            await ctx.send(f"{self.bot.config.error} A playlist named `{name}` already exists.")
            return
        self.bot.playlist_loader.create_playlist(name)
        await ctx.send(f"{self.bot.config.success} Created playlist `{name}`.")

    @playlist.command(name="delete", help="Deletes a playlist")
    async def playlist_delete(self, ctx: commands.Context, *, name: str = "") -> None:
        if not name:
            await ctx.send(f"{self.bot.config.error} Please provide a playlist name.")
            return
        name = name.replace(" ", "_")
        if name not in self.bot.playlist_loader.get_playlist_names():
            await ctx.send(f"{self.bot.config.error} No playlist named `{name}` exists.")
            return
        self.bot.playlist_loader.delete_playlist(name)
        await ctx.send(f"{self.bot.config.success} Deleted playlist `{name}`.")

    @playlist.command(name="append", help="Appends a URL to a playlist")
    async def playlist_append(self, ctx: commands.Context, name: str = "", *, url: str = "") -> None:
        if not name or not url:
            await ctx.send(f"{self.bot.config.error} Usage: `{ctx.prefix}playlist append <name> <URL>`")
            return
        name = name.replace(" ", "_")
        if name not in self.bot.playlist_loader.get_playlist_names():
            await ctx.send(f"{self.bot.config.error} No playlist named `{name}` exists.")
            return
        self.bot.playlist_loader.append_to_playlist(name, url)
        await ctx.send(f"{self.bot.config.success} Appended to playlist `{name}`.")

    @playlist.command(name="write", help="Overwrites a playlist with new content")
    async def playlist_write(self, ctx: commands.Context, name: str = "", *, content: str = "") -> None:
        if not name or not content:
            await ctx.send(f"{self.bot.config.error} Usage: `{ctx.prefix}playlist write <name> <content>`")
            return
        name = name.replace(" ", "_")
        if name not in self.bot.playlist_loader.get_playlist_names():
            await ctx.send(f"{self.bot.config.error} No playlist named `{name}` exists.")
            return
        self.bot.playlist_loader.write_playlist(name, content)
        await ctx.send(f"{self.bot.config.success} Wrote to playlist `{name}`.")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(PlaylistCog(bot))
