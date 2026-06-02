from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.dj_command import is_dj
from commands.music_command import music_check
if TYPE_CHECKING:
    from bot import MusicBot

class RepeatCog(commands.Cog, name="DJ"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="repeat", help="Cycles repeat mode: Off → All → Single")
    @commands.guild_only()
    @is_dj()
    async def repeat(self, ctx: commands.Context) -> None:
        if not await music_check(ctx, be_listening=True):
            return
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        new_mode = settings.repeat_mode.next()
        settings.set_repeat_mode(new_mode)
        emoji = new_mode.emoji or ""
        await ctx.send(f"{self.bot.config.success} Repeat mode set to **{new_mode.label}** {emoji}".strip())

async def setup(bot: "MusicBot") -> None:
    cog = RepeatCog(bot)
    cog.repeat.aliases = bot.config.get_aliases("repeat")
    await bot.add_cog(cog)
