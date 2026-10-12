from __future__ import annotations
from typing import TYPE_CHECKING
import discord
from discord.ext import commands
from commands.admin_command import is_admin
from utils.format_util import list_of_roles
if TYPE_CHECKING:
    from bot import MusicBot

class SetdjCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setdj", usage="<role | NONE>", help="Sets the DJ role for this server")
    @commands.guild_only()
    @is_admin()
    async def setdj(self, ctx: commands.Context, *, role_name: str = "") -> None:
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        if not role_name or role_name.lower() == "none":
            settings.set_dj_role(None)
            await ctx.send(f"{self.bot.config.success} DJ role cleared.")
            return
        if ctx.message.role_mentions:
            role = ctx.message.role_mentions[0]
        else:
            matches = [r for r in ctx.guild.roles if r.name.lower() == role_name.lower()]
            if not matches:
                await ctx.send(f"{self.bot.config.error} No role found matching `{role_name}`.")
                return
            if len(matches) > 1:
                await ctx.send(self.bot.config.warning + list_of_roles(matches, role_name))
                return
            role = matches[0]
        settings.set_dj_role(role)
        await ctx.send(f"{self.bot.config.success} DJ role set to **{role.name}**.")

async def setup(bot: "MusicBot") -> None:
    cog = SetdjCog(bot)
    cog.setdj.aliases = bot.config.get_aliases("setdj")
    await bot.add_cog(cog)
