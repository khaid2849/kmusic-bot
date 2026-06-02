import asyncio
import logging
import sys

from config import BotConfig
from bot import MusicBot


def setup_logging(level: str) -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1].lower() == "generate-config":
        BotConfig.write_default_config()
        return

    config = BotConfig()
    config.load()

    if not config.is_valid:
        sys.exit(1)

    setup_logging(config.log_level)
    log = logging.getLogger("main")
    log.info("Starting MusicBot...")

    bot = MusicBot(config)

    try:
        await bot.start(config.token)
    except KeyboardInterrupt:
        pass
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
