from __future__ import annotations
from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot import MusicBot


async def check_dj_permission(ctx: commands.Context) -> bool:
    bot: "MusicBot" = ctx.bot
    if ctx.author.id == bot.config.owner:
        return True
    if not ctx.guild:
        return True
    if ctx.author.guild_permissions.manage_guild:
        return True
    settings  = bot.settings_manager.get_settings(ctx.guild.id)
    dj_role   = settings.get_role(ctx.guild)
    if dj_role is None:
        return False
    return dj_role in ctx.author.roles or dj_role.id == ctx.guild.id


def is_dj():
    async def predicate(ctx: commands.Context) -> bool:
        if not await check_dj_permission(ctx):
            await ctx.send(f"{ctx.bot.config.error} Only DJs can use that command!")
            return False
        return True
    return commands.check(predicate)
