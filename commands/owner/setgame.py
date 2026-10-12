from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.owner_command import is_owner
from utils.other_util import parse_game
if TYPE_CHECKING:
    from bot import MusicBot

class SetgameCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setgame", usage="<activity>", help="Changes the bot's activity (e.g. 'playing Music')")
    @is_owner()
    async def setgame(self, ctx: commands.Context, *, game: str = "") -> None:
        activity = parse_game(game) if game else None
        await self.bot.change_presence(activity=activity)
        if not game or game.lower() == "none":
            await ctx.send(f"{self.bot.config.success} Removed the activity status.")
        else:
            await ctx.send(f"{self.bot.config.success} Activity set to `{game}`.")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(SetgameCog(bot))
