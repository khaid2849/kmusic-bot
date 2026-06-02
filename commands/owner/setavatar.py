from __future__ import annotations
from typing import TYPE_CHECKING
import httpx
from discord.ext import commands
from commands.owner_command import is_owner
if TYPE_CHECKING:
    from bot import MusicBot

class SetavatarCog(commands.Cog, name="Owner"):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    @commands.command(name="setavatar", help="Changes the bot's avatar")
    @is_owner()
    async def setavatar(self, ctx: commands.Context, url: str = "") -> None:
        if not url and ctx.message.attachments:
            url = ctx.message.attachments[0].url
        if not url:
            await ctx.send(f"{self.bot.config.error} Please provide an image URL or attach an image.")
            return
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url)
            await self.bot.user.edit(avatar=response.content)
            await ctx.send(f"{self.bot.config.success} Avatar updated.")
        except Exception as e:
            await ctx.send(f"{self.bot.config.error} Failed to update avatar: {e}")

async def setup(bot: "MusicBot") -> None:
    await bot.add_cog(SetavatarCog(bot))
