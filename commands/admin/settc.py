from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.admin_command import is_admin
from utils.format_util import list_of_text_channels
if TYPE_CHECKING:
    from bot import MusicBot

class SettcCog(commands.Cog, name="Admin"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="settc", help="Restricts music commands to a specific text channel")
    @commands.guild_only()
    @is_admin()
    async def settc(self, ctx: commands.Context, *, channel_name: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not channel_name or channel_name.lower() == "none":
            settings.set_text_channel(None)
            await ctx.send(f"{self.bot.config.success} Text channel restriction cleared.")
            return
        if ctx.message.channel_mentions:
            channel = ctx.message.channel_mentions[0]
        else:
            matches = [c for c in ctx.guild.text_channels if c.name.lower() == channel_name.lower()]
            if not matches:
                await ctx.send(f"{self.bot.config.error} No text channel found matching `{channel_name}`.")
                return
            if len(matches) > 1:
                await ctx.send(self.bot.config.warning + list_of_text_channels(matches, channel_name))
                return
            channel = matches[0]
        settings.set_text_channel(channel)
        await ctx.send(f"{self.bot.config.success} Music commands restricted to {channel.mention}.")

async def setup(bot: "MusicBot") -> None:
    cog = SettcCog(bot)
    cog.settc.aliases = bot.config.get_aliases("settc")
    await bot.add_cog(cog)
