from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
if TYPE_CHECKING:
    from bot import MusicBot

class SettingsCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="settings", aliases=["status"], help="Shows the current server settings")
    @commands.guild_only()
    async def settings(self, ctx: commands.Context) -> None:
        s    = self.bot.settings_manager.get_settings(ctx.guild.id)
        cfg  = self.bot.config
        tc   = s.get_text_channel(ctx.guild)
        vc   = s.get_voice_channel(ctx.guild)
        role = s.get_role(ctx.guild)
        skip_pct = (
            f"{int(s.skip_ratio * 100)}%" if s.skip_ratio != -1
            else f"Default ({int(cfg.skip_ratio * 100)}%)"
        )
        prefix_str = f"`{s.prefix}`" if s.prefix else f"Default (`{cfg.prefix}`)"

        embed = discord.Embed(title=f"{ctx.guild.name} Settings", color=ctx.guild.me.color)
        embed.add_field(name="Prefix",           value=prefix_str,                                  inline=True)
        embed.add_field(name="Text Channel",     value=tc.mention if tc else "Any",                  inline=True)
        embed.add_field(name="Voice Channel",    value=vc.name    if vc else "Any",                  inline=True)
        embed.add_field(name="DJ Role",          value=role.mention if role else "None",              inline=True)
        embed.add_field(name="Volume",           value=str(s.volume),                                inline=True)
        embed.add_field(name="Repeat Mode",      value=s.repeat_mode.label,                          inline=True)
        embed.add_field(name="Queue Type",       value=s.queue_type.label,                           inline=True)
        embed.add_field(name="Skip Ratio",       value=skip_pct,                                     inline=True)
        embed.add_field(name="Default Playlist", value=f"`{s.default_playlist}`" if s.default_playlist else "None", inline=True)
        await ctx.send(embed=embed)

async def setup(bot: "MusicBot") -> None:
    cog = SettingsCog(bot)
    cog.settings.aliases = bot.config.get_aliases("settings") or ["status"]
    await bot.add_cog(cog)
