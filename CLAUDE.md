# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the bot (requires Lavalink running first)
java -jar lavalink/Lavalink.jar   # Terminal 1
python3 main.py                   # Terminal 2

# Generate a default config.toml without starting the bot
python3 main.py generate-config

# Run all tests
python3 -m pytest tests/ -v

# Run a single test file
python3 -m pytest tests/test_fair_queue.py -v
```

## Architecture

The bot is a `discord.py` prefix-command bot that uses **Lavalink** (via the `wavelink` library) as its audio backend. Lavalink must be running as a separate Java process on `localhost:2333` before the bot starts.

### Startup flow

`main.py` → loads `BotConfig` from `config.toml` → creates `MusicBot` → `setup_hook` initializes subsystems → loads all cogs (commands + listeners).

### Core subsystems (all hung off `bot.*`)

| Attribute | Class | Responsibility |
|---|---|---|
| `bot.settings_manager` | `SettingsManager` | Loads/saves per-guild settings from `serversettings.json` |
| `bot.player_manager` | `PlayerManager` | Manages the Lavalink node connection and a registry of `AudioHandler` per guild |
| `bot.playlist_loader` | `PlaylistLoader` | Reads local `.txt` playlist files from the `Playlists/` folder |
| `bot.nowplaying_handler` | `NowplayingHandler` | Auto-refreshes the "Now Playing" embed in Discord |
| `bot.alone_in_voice_handler` | `AloneInVoiceHandler` | Auto-leaves voice when the bot is alone |

### Per-guild audio flow

1. A user runs a music command → `music_check()` in `commands/music_command.py` validates voice/text channel constraints and calls `player_manager.setup_handler(guild)`.
2. `PlayerManager.setup_handler` creates an `AudioHandler` wrapping a `wavelink.Player`. The handler is stored in `_handlers[guild_id]`.
3. `AudioHandler` owns the queue (`AbstractQueue`) and manages playback. When a track ends, `on_track_end` pulls the next item from the queue (respecting repeat mode), or falls back to the guild's default playlist, or disconnects.
4. Wavelink fires `on_wavelink_track_start` / `on_wavelink_track_end` events, received by `BotListeners` (in `listeners.py`), which delegate to the appropriate `AudioHandler`.

### Queue system

`AbstractQueue` (`trackqueue/abstract_queue.py`) is the base with shared operations (`pull`, `add_at`, `remove`, `shuffle`, `clear`). Two concrete implementations:

- **`LinearQueue`** — standard FIFO; `add()` appends to the end.
- **`FairQueue`** — interleaves tracks by requester so no single user monopolizes the queue. `add()` inserts after the last track by the same user but before the first repeat of any user in the subsequent block.

Queue type is per-guild and stored in `serversettings.json`. Switching queue type (via `queuetype` command) migrates existing items by calling `qt.create_instance(existing_queue)`.

> The package is named `trackqueue/` (not `queue/`) to avoid shadowing Python's built-in `queue` module, which `concurrent.futures` depends on internally.

### Permission tiers

Commands use decorator-based checks applied in each cog file:

| Tier | Check source |
|---|---|
| Everyone | `music_check()` in `commands/music_command.py` |
| DJ | `is_dj()` decorator from `commands/dj_command.py` |
| Admin | `commands.has_guild_permissions(manage_guild=True)` |
| Owner | `commands.is_owner()` via `owner_command.py` |

When no DJ role is set, **no one** (except admins/owner) can use DJ commands.

### Settings persistence

`SettingsManager` writes `serversettings.json` to the working directory. `Settings` objects call `_manager.write_settings()` whenever a field is changed (via property setters in `settings/settings.py`). Only non-default values are serialized.

### Config

`config.py` reads `config.toml` (or prompts interactively if missing/empty). `BotConfig` exposes typed fields used throughout the bot. `[aliases]` in config maps command names to alias lists; `[transforms]` supports regex URL rewriting before passing to Lavalink.
