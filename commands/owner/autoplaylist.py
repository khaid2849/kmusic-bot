from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

class AutoplaylistCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="autoplaylist", usage="<playlist | NONE>", help="Sets the default playlist for this server")
    @commands.guild_only()
    @is_owner()
    async def autoplaylist(self, ctx: commands.Context, *, name: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not name or name.lower() == "none":
            settings.set_default_playlist(None)
            await ctx.send(f"{self.bot.config.success} Default playlist cleared for **{ctx.guild.name}**.")
            return
        pname = name.replace(" ", "_")
        if self.bot.playlist_loader.get_playlist(pname) is None:
            await ctx.send(f"{self.bot.config.error} No playlist named `{pname}` found in the Playlists folder.")
            return
        settings.set_default_playlist(pname)
        await ctx.send(f"{self.bot.config.success} Default playlist for **{ctx.guild.name}** set to `{pname}`.")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(AutoplaylistCog(bot))
