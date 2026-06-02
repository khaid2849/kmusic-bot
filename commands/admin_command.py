from __future__ import annotations
from discord.ext import commands


def is_admin():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id == ctx.bot.config.owner:
            return True
        if ctx.author.guild_permissions.manage_guild:
            return True
        await ctx.send(f"{ctx.bot.config.error} You must have the Manage Server permission to use that!")
        return False
    return commands.check(predicate)
