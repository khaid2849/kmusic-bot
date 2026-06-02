import discord
import httpx

CURRENT_VERSION = "1.0.0"
GITHUB_REPO = "jagrosh/MusicBot"
NEW_VERSION_AVAILABLE = (
    "There is a new version of JMusicBot available!\n"
    "Current version: {}\nNew version: {}\n"
    "Please visit https://github.com/jagrosh/MusicBot/releases/latest"
)


def parse_game(game: str) -> discord.Activity | None:
    if not game or game.strip().lower() in ("default", ""):
        return None
    lower = game.lower().strip()
    if lower == "none":
        return None
    if lower.startswith("playing "):
        return discord.Game(name=game[8:].strip() or "​")
    if lower.startswith("listening to "):
        return discord.Activity(type=discord.ActivityType.listening, name=game[13:].strip() or "​")
    if lower.startswith("listening "):
        return discord.Activity(type=discord.ActivityType.listening, name=game[10:].strip() or "​")
    if lower.startswith("watching "):
        return discord.Activity(type=discord.ActivityType.watching, name=game[9:].strip() or "​")
    if lower.startswith("streaming "):
        parts = game[10:].strip().split(None, 1)
        if len(parts) == 2:
            return discord.Streaming(name=parts[1], url=f"https://twitch.tv/{parts[0]}")
    return discord.Game(name=game.strip() or "​")


def parse_status(status: str) -> discord.Status:
    mapping = {
        "online":    discord.Status.online,
        "idle":      discord.Status.idle,
        "dnd":       discord.Status.dnd,
        "invisible": discord.Status.invisible,
    }
    return mapping.get(status.lower().strip(), discord.Status.online)


async def get_latest_version() -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest")
            return r.json().get("tag_name")
    except Exception:
        return None


def get_current_version() -> str:
    return CURRENT_VERSION


async def check_unsupported_bot(bot: discord.Client) -> str | None:
    if discord.UserFlags.verified_bot in bot.user.public_flags:
        return "The bot is verified. Using this bot as a verified bot is not supported."
    try:
        app = await bot.application_info()
        if app.bot_public:
            return (
                '"Public Bot" is enabled. Please disable it at '
                f"https://discord.com/developers/applications/{bot.user.id}/bot"
            )
    except Exception:
        pass
    return None
