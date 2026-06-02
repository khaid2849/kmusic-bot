from __future__ import annotations
import sys
from typing import TYPE_CHECKING
import discord
import wavelink
from discord.ext import commands
from commands.owner_command import is_owner
from utils.other_util import get_current_version
if TYPE_CHECKING:
    from bot import MusicBot

class DebugCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="debug", help="Shows runtime debug information")
    @is_owner()
    async def debug(self, ctx: commands.Context) -> None:
        active_voice = sum(1 for g in self.bot.guilds if g.voice_client and g.voice_client.connected)
        try:
            node = wavelink.Pool.get_node()
            node_status = f"Connected ({node.uri})"
        except Exception:
            node_status = "Not connected"

        embed = discord.Embed(title="Debug Info", color=discord.Color.blurple())
        embed.add_field(name="Bot Version",      value=get_current_version(),         inline=True)
        embed.add_field(name="Python",           value=sys.version.split()[0],        inline=True)
        embed.add_field(name="discord.py",       value=discord.__version__,           inline=True)
        embed.add_field(name="wavelink",         value=wavelink.__version__,          inline=True)
        embed.add_field(name="Guilds",           value=str(len(self.bot.guilds)),      inline=True)
        embed.add_field(name="Voice Connections",value=str(active_voice),             inline=True)
        embed.add_field(name="Lavalink Node",    value=node_status,                   inline=False)
        await ctx.send(embed=embed)

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(DebugCog(bot))
