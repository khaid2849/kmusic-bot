from __future__ import annotations
from typing import TYPE_CHECKING
from discord.ext import commands
from commands.admin_command import is_admin
from settings.queue_type import QueueType
if TYPE_CHECKING:
    from bot import MusicBot

class QueuetypeCog(commands.Cog, name="Admin"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="queuetype", help="Sets the queue type: fair or linear")
    @commands.guild_only()
    @is_admin()
    async def queuetype(self, ctx: commands.Context, *, value: str = "") -> None:
        if not value or value.lower() not in QueueType.names():
            await ctx.send(f"{self.bot.config.error} Valid queue types: {', '.join(QueueType.names())}.")
            return
        qt = QueueType.from_str(value)
        settings = self.bot.settings_manager.get_settings(ctx.guild.id)
        settings.set_queue_type(qt)
        if self.bot.player_manager.has_handler(ctx.guild):
            handler = self.bot.player_manager.get_handler(ctx.guild)
            if handler:
                handler.set_queue_type(qt)
        await ctx.send(f"{self.bot.config.success} Queue type set to **{qt.label}** {qt.emoji}.")

async def setup(bot: "MusicBot") -> None:
    cog = QueuetypeCog(bot)
    cog.queuetype.aliases = bot.config.get_aliases("queuetype")
    await bot.add_cog(cog)
