from __future__ import annotations
from discord.ext import commands


def is_owner():
    async def predicate(ctx: commands.Context) -> bool:
        if ctx.author.id == ctx.bot.config.owner:
            return True
        await ctx.send(f"{ctx.bot.config.error} Only the bot owner can use that command!")
        return False
    return commands.check(predicate)
