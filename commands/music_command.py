from __future__ import annotations
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands

if TYPE_CHECKING:
    from bot import MusicBot


async def music_check(ctx: commands.Context, be_playing: bool = False, be_listening: bool = False) -> bool:
    bot: "MusicBot" = ctx.bot
    settings = bot.settings_manager.get_settings(ctx.guild.id)

    # Enforce locked text channel
    tc = settings.get_text_channel(ctx.guild)
    if tc and ctx.channel != tc:
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        try:
            await ctx.author.send(f"{bot.config.error} You can only use that command in {tc.mention}!")
        except discord.Forbidden:
            pass
        return False

    # Ensure handler exists
    await bot.player_manager.setup_handler(ctx.guild)

    player: wavelink.Player | None = ctx.voice_client  # type: ignore

    if be_playing:
        if not player or not player.current:
            await ctx.send(f"{bot.config.error} There must be music playing to use that!")
            return False

    if be_listening:
        bot_channel = player.channel if player and player.connected else None
        if not bot_channel:
            bot_channel = settings.get_voice_channel(ctx.guild)

        member_vc = ctx.author.voice
        if not member_vc or not member_vc.channel:
            in_ch = f"in {bot_channel.mention}" if bot_channel else "in a voice channel"
            await ctx.send(f"{bot.config.error} You must be listening {in_ch} to use that!")
            return False

        if member_vc.deaf:
            await ctx.send(f"{bot.config.error} You must be listening (not deafened) to use that!")
            return False

        afk = ctx.guild.afk_channel
        if afk and member_vc.channel == afk:
            await ctx.send(f"{bot.config.error} You cannot use that command in an AFK channel!")
            return False

        if bot_channel and member_vc.channel != bot_channel:
            await ctx.send(f"{bot.config.error} You must be listening in {bot_channel.mention} to use that!")
            return False

        # Auto-join if not connected
        if not player or not player.connected:
            try:
                await ctx.author.voice.channel.connect(cls=wavelink.Player)
                await bot.player_manager.setup_handler(ctx.guild)
            except Exception:
                await ctx.send(f"{bot.config.error} I am unable to connect to {member_vc.channel.mention}!")
                return False

    return True
