from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.admin_command import is_admin
from utils.format_util import list_of_voice_channels
if TYPE_CHECKING:
    from bot import MusicBot

class SetvcCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setvc", usage="<channel | NONE>", help="Restricts the bot to a specific voice channel")
    @commands.guild_only()
    @is_admin()
    async def setvc(self, ctx: commands.Context, *, channel_name: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not channel_name or channel_name.lower() == "none":
            settings.set_voice_channel(None)
            await ctx.send(f"{self.bot.config.success} Voice channel restriction cleared.")
            return
        matches = [c for c in ctx.guild.voice_channels if c.name.lower() == channel_name.lower()]
        if not matches:
            await ctx.send(f"{self.bot.config.error} No voice channel found matching `{channel_name}`.")
            return
        if len(matches) > 1:
            await ctx.send(self.bot.config.warning + list_of_voice_channels(matches, channel_name))
            return
        settings.set_voice_channel(matches[0])
        await ctx.send(f"{self.bot.config.success} I will now only operate in **{matches[0].name}**.")

async def setup(bot: "MusicBot") -> None:
    cog = SetvcCog(bot)
    cog.setvc.aliases = bot.config.get_aliases("setvc")
    await bot.add_cog(cog)
