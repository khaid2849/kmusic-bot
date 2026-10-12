from __future__ import annotations
import math
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from commands.music_command import music_check
from utils.time_util import format_time

if TYPE_CHECKING:
    from bot import MusicBot

_PER_PAGE = 10


class QueueView(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], timeout: float = 120):
        super().__init__(timeout=timeout)
        self.pages   = pages
        self.current = 0
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.prev_btn.disabled = self.current == 0
        self.next_btn.disabled = self.current >= len(self.pages) - 1

    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def prev_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current = max(0, self.current - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="▶", style=discord.ButtonStyle.secondary)
    async def next_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current = min(len(self.pages) - 1, self.current + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)


class QueueCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="queue", usage="[page]", aliases=["list"], help="Shows the current queue")
    @commands.guild_only()
    async def queue(self, ctx: commands.Context, page: int = 1) -> None:
        if not await music_check(ctx):
            return
        handler = self.bot.player_manager.get_handler(ctx.guild)
        if not handler:
            await ctx.send(f"{self.bot.config.error} Nothing is in the queue.")
            return

        player  = ctx.voice_client
        q_list  = handler.get_queue().get_list()
        current = player.current if player else None

        if not current and not q_list:
            await ctx.send(f"{self.bot.config.error} There is no music in the queue!")
            return

        total_duration = sum(t.track.length or 0 for t in q_list)
        total_pages    = max(1, math.ceil(len(q_list) / _PER_PAGE))
        pages: list[discord.Embed] = []

        for p in range(total_pages):
            embed = discord.Embed(color=ctx.guild.me.color)
            embed.set_author(name=f"Queue for {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

            if current and p == 0:
                embed.description = f"**Now Playing:**\n{current.title}\n\n**Up Next:**"

            start = p * _PER_PAGE
            chunk = q_list[start: start + _PER_PAGE]
            lines = [f"`{start + i + 1}.` {str(qt)}" for i, qt in enumerate(chunk)]
            embed.description = (embed.description or "") + "\n" + "\n".join(lines) if lines else (embed.description or "The queue is empty.")

            embed.set_footer(text=f"Page {p + 1}/{total_pages} | {len(q_list)} tracks | {format_time(total_duration)} total")
            pages.append(embed)

        page = max(1, min(page, total_pages)) - 1
        view = QueueView(pages) if len(pages) > 1 else None
        await ctx.send(embed=pages[page], view=view)


async def setup(bot: "MusicBot") -> None:
    cog = QueueCog(bot)
    cog.queue.aliases = bot.config.get_aliases("queue") or ["list"]
    await bot.add_cog(cog)
