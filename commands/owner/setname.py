from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

class SetnameCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setname", help="Changes the bot's username")
    @is_owner()
    async def setname(self, ctx: commands.Context, *, name: str = "") -> None:
        if not name:
            await ctx.send(f"{self.bot.config.error} Please provide a new name.")
            return
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"{self.bot.config.success} Name changed to **{name}**.")
        except Exception as e:
            await ctx.send(f"{self.bot.config.error} Failed to change name: {e}\n*(Note: username can only be changed twice per hour)*")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(SetnameCog(bot))
