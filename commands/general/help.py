from __future__ import annotations
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from bot import MusicBot

# Section order and titles, keyed by the commands.<category> package a cog lives in
CATEGORIES = [
    ("music",   "🎵 Music"),
    ("dj",      "🎧 DJ (DJ role or admins)"),
    ("admin",   "🛠️ Admin (Manage Server)"),
    ("general", "ℹ️ General"),
    ("owner",   "👑 Owner"),
]


def _category(command: commands.Command) -> str | None:
    parts = (command.module or "").split(".")
    return parts[1] if len(parts) >= 3 and parts[0] == "commands" else None


class HelpCog(commands.Cog):
    def __init__(self, bot: "MusicBot"):
        self.bot = bot

    def _prefix(self, ctx: commands.Context) -> str:
        if ctx.guild:
            guild_prefix = self.bot.settings_manager.get_settings(ctx.guild.id).prefix
            if guild_prefix:
                return guild_prefix
        if self.bot.config.prefix == "@mention":
            return f"@{self.bot.user.name} "
        return self.bot.config.prefix

    def _usage(self, prefix: str, command: commands.Command) -> str:
        return f"{prefix}{command.qualified_name} {command.usage or command.signature}".strip()

    @commands.command(name="help", usage="[command]", help="Shows all commands, or details about one command")
    async def help_cmd(self, ctx: commands.Context, *, command_name: str = "") -> None:
        prefix   = self._prefix(ctx)
        is_owner = await self.bot.is_owner(ctx.author)

        if command_name:
            command = self.bot.get_command(command_name.removeprefix(prefix).strip())
            if not command or command.hidden or (_category(command) == "owner" and not is_owner):
                await ctx.send(f"{self.bot.config.error} No command called `{command_name}`. "
                               f"Use `{prefix}{ctx.invoked_with}` to see all commands.")
                return
            embed = discord.Embed(title=f"`{self._usage(prefix, command)}`",
                                  description=command.help or "No description.",
                                  color=discord.Color.blue())
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{prefix}{a}`" for a in command.aliases))
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"{self.bot.user.name} commands",
            description=f"Prefix: `{prefix}` · `<required>` `[optional]`\n"
                        f"Use `{prefix}{ctx.invoked_with} <command>` for details.",
            color=discord.Color.blue(),
        )
        for key, heading in CATEGORIES:
            if key == "owner" and not is_owner:
                continue
            cmds = sorted((c for c in self.bot.commands if _category(c) == key and not c.hidden),
                          key=lambda c: c.name)
            lines = [f"`{self._usage(prefix, c)}` — {c.help or ''}" for c in cmds]
            self._add_section(embed, heading, lines)

        await ctx.send(embed=embed)

    @staticmethod
    def _add_section(embed: discord.Embed, heading: str, lines: list[str]) -> None:
        # Embed field values are capped at 1024 chars, so long sections spill into extra fields
        chunk = ""
        for line in lines:
            if chunk and len(chunk) + len(line) + 1 > 1024:
                embed.add_field(name=heading, value=chunk, inline=False)
                heading, chunk = "​", ""
            chunk = f"{chunk}\n{line}" if chunk else line
        if chunk:
            embed.add_field(name=heading, value=chunk, inline=False)


async def setup(bot: "MusicBot") -> None:
    cog = HelpCog(bot)
    cog.help_cmd.name    = bot.config.help or "help"
    cog.help_cmd.aliases = bot.config.get_aliases("help")
    await bot.add_cog(cog)
