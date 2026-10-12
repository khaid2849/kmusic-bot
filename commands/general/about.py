from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from utils.other_util import get_current_version
if TYPE_CHECKING:
    from bot import MusicBot

class AboutCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="about", help="Shows information about the bot")
    async def about(self, ctx: commands.Context) -> None:
        embed = discord.Embed(
            title=f"About {self.bot.user.name}",
            description="A music bot that is easy to host yourself!",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Version",  value=get_current_version(), inline=True)
        embed.add_field(name="Guilds",   value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Features", inline=False,
            value="🎵 High-quality music playback\n🔢 FairQueue™ Technology\n🏠 Easy to host yourself")
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(AboutCog(bot))
