import discord


def progress_bar(percent: float) -> str:
    bar = ""
    for i in range(12):
        bar += "🔘" if i == int(percent * 12) else "▬"
    return bar


def volume_icon(volume: int) -> str:
    if volume == 0:   return "🔇"
    if volume < 30:   return "🔈"
    if volume < 70:   return "🔉"
    return "🔊"


def filter_text(text: str) -> str:
    return (
        text.replace("‮", "")
            .replace("@everyone", "@еveryone")
            .replace("@here",     "@hеre")
            .strip()
    )


def format_username(user: discord.User | discord.Member) -> str:
    discrim = getattr(user, "discriminator", "0")
    if not discrim or discrim == "0":
        return user.name
    return f"{user.name}#{discrim}"


def list_of_text_channels(channels: list[discord.TextChannel], query: str) -> str:
    out = f' Multiple text channels found matching "{query}":'
    for ch in channels[:6]:
        out += f"\n - {ch.name} ({ch.mention})"
    if len(channels) > 6:
        out += f"\n**And {len(channels) - 6} more...**"
    return out


def list_of_voice_channels(channels: list[discord.VoiceChannel], query: str) -> str:
    out = f' Multiple voice channels found matching "{query}":'
    for ch in channels[:6]:
        out += f"\n - {ch.name} (ID:{ch.id})"
    if len(channels) > 6:
        out += f"\n**And {len(channels) - 6} more...**"
    return out


def list_of_roles(roles: list[discord.Role], query: str) -> str:
    out = f' Multiple roles found matching "{query}":'
    for r in roles[:6]:
        out += f"\n - {r.name} (ID:{r.id})"
    if len(roles) > 6:
        out += f"\n**And {len(roles) - 6} more...**"
    return out
