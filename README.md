# 🎵 Discord Music Bot (Python)

A self-hosted Discord music bot built with **Python**, **discord.py**, and **Lavalink**. Preserving all features including FairQueue™ technology, multi-source audio playback, per-guild settings, and local playlist support.

---

## Features

- 🎶 High-quality audio via **Lavalink** (YouTube, SoundCloud, Bandcamp, Vimeo, Twitch, and more)
- 🔢 **FairQueue™** — interleaves tracks by requester so no single user monopolizes the queue
- 📋 Local playlist files (`.txt`) with shuffle support
- 🔁 Repeat modes: Off, All, Single
- 🔊 Per-guild volume, prefix, DJ role, text/voice channel locks, skip ratio
- ⏩ Linear or Fair queue type, switchable per guild
- 🔒 Four-tier permission system: Everyone → DJ → Admin → Owner
- 💾 Persistent per-guild settings (`serversettings.json`)
- 🔐 Discord DAVE end-to-end voice encryption (supported via discord.py)

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10+ |
| Java | 17+ (for Lavalink server only) |
| FFmpeg | Latest stable |
| Docker | Any recent version (for the YouTube cipher server) |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/khaid2849/kmusic-bot.git
cd kmusic-bot
```

### 2. Install Python dependencies

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

### 3. Download Lavalink

Download the latest `Lavalink.jar` from the [Lavalink releases page](https://github.com/lavalink-devs/Lavalink/releases) and place it in the `lavalink/` folder:

```
lavalink/
├── Lavalink.jar        ← place here
└── application.yml     ← already included
```

Lavalink downloads the YouTube plugin into `lavalink/plugins/` automatically on first start.

### 4. Set up YouTube playback

YouTube regularly changes how its streams are protected, so playing from YouTube needs two extra pieces.
SoundCloud, Bandcamp, Twitch and Vimeo work without them.

**a) Remote cipher server** ([yt-cipher](https://github.com/kikkia/yt-cipher)) decodes YouTube's stream signatures:

```bash
docker run -d --name yt-cipher --restart unless-stopped \
  -p 127.0.0.1:8001:8001 \
  -e OVERRIDE_PLAYER_VARIANT=IAS \
  -e API_TOKEN=<choose-a-password> \
  ghcr.io/kikkia/yt-cipher:master
```

`lavalink/application.yml` already points to `http://127.0.0.1:8001`. Give Lavalink the same password through an
environment variable (it is deliberately not stored in the repo):

```bash
PLUGINS_YOUTUBE_REMOTECIPHER_PASSWORD=<choose-a-password>
```

**b) YouTube OAuth (recommended)**: many videos now require a signed-in client. Start Lavalink once with
`skipInitialization: false` under `plugins.youtube.oauth` in `application.yml`, follow the device-login link it prints
(use a spare Google account, not your main one), and copy the refresh token it logs. Then set:

```bash
PLUGINS_YOUTUBE_OAUTH_REFRESHTOKEN=<refresh-token>
```

Put both variables in `~/.config/kmusic/lavalink.env` (`chmod 600` it). The service files in `deploy/` load that file
automatically; when running Lavalink by hand, `export` them first.

> `application.yml` pins a **snapshot** build of the YouTube plugin that contains a fix for the `TV` client
> ([youtube-source#226](https://github.com/lavalink-devs/youtube-source/issues/226)). Switch back to a release
> (`snapshot: false`) once a version newer than 1.18.2 is published.

### 5. Configure the bot

Copy the example config and fill in your values:

```bash
cp config.toml.example config.toml
```

Open `config.toml` and set at minimum:

```toml
token = "YOUR_BOT_TOKEN_HERE"
owner = 123456789012345678   # your Discord user ID
```

See the [Configuration](#configuration) section for all available options.

> **First run:** If `config.toml` is missing or the token/owner fields are empty, the bot will prompt you for them interactively in the terminal.

---

## Running the Bot

Two processes must run simultaneously — the Lavalink audio server and the Python bot.

**Terminal 1 — Start Lavalink:**
```bash
java -jar lavalink/Lavalink.jar
```

**Terminal 2 — Start the bot:**
```bash
venv/bin/python main.py
```

### Run as a service (start on boot, restart on crash)

Templates for systemd user services are in `deploy/`. They assume the repo lives at `~/kmusic-bot`; edit the paths
otherwise.

```bash
mkdir -p ~/.config/systemd/user
cp deploy/kmusic-lavalink.service deploy/kmusic-bot.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now kmusic-lavalink kmusic-bot
sudo loginctl enable-linger "$USER"     # keep services running without an active login

journalctl --user -u kmusic-bot -f       # follow the bot's logs
systemctl --user restart kmusic-bot      # apply config.toml changes
```

### Generate a default config without starting the bot

```bash
python3 main.py generate-config
```

### Run tests

```bash
python3 -m pytest tests/ -v
```

---

## Configuration

All settings are in `config.toml`. A fully documented example is provided in `config.toml.example`.

| Key | Default | Description |
|---|---|---|
| `token` | required | Discord bot token |
| `owner` | required | Bot owner Discord user ID |
| `prefix` | `"@mention"` | Command prefix (`"!"`, `"!!"`, etc.) |
| `altprefix` | `"NONE"` | Optional secondary prefix |
| `game` | `"DEFAULT"` | Bot activity (`"playing Music"`, `"watching X"`, `"none"`) |
| `status` | `"online"` | Online status: `online`, `idle`, `dnd`, `invisible` |
| `song_in_status` | `false` | Show current song title in bot status |
| `np_images` | `false` | Show thumbnails in Now Playing embed (disables auto-refresh) |
| `stay_in_channel` | `false` | Stay in voice channel after queue ends |
| `max_time` | `0` | Max track length in seconds (0 = unlimited) |
| `max_yt_playlist_pages` | `10` | Max YouTube playlist pages to load (100 tracks/page) |
| `skip_ratio` | `0.55` | Default vote-skip ratio (55% of listeners must vote) |
| `alone_time_until_stop` | `0` | Seconds alone in voice before leaving (0 = never) |
| `idle_time_until_leave` | `0` | Seconds to stay in voice while nothing plays (queue ended or paused) before leaving. `0` = leave as soon as the queue ends |
| `help` | `"help"` | Name of the help command |
| `playlists_folder` | `"Playlists"` | Folder for local playlist `.txt` files |
| `update_alerts` | `true` | DM owner when a new version is available |
| `log_level` | `"info"` | Logging level: `debug`, `info`, `warning`, `error` |

### Aliases

You can configure custom aliases for any command under `[aliases]` in `config.toml`:

```toml
[aliases]
play      = ["p"]
skip      = ["s", "voteskip"]
nowplaying = ["np", "current"]
```

### Local Playlists

Create `.txt` files in the `Playlists/` folder. Each line is a URL or search query. Lines starting with `#` or `//` are comments. Add `#shuffle` on its own line to shuffle the playlist on load.

```
# My Playlist
https://www.youtube.com/watch?v=...
lofi hip hop radio
#shuffle
```

---

## Commands

### 🎵 Music (Everyone)

| Command | Description |
|---|---|
| `play <title\|URL>` | Plays a song by title or URL |
| `play playlist <name>` | Plays a local playlist from the Playlists folder |
| `nowplaying` | Shows the currently playing song |
| `queue [page]` | Shows the current queue |
| `skip` | Votes to skip the current song |
| `search <query>` | Searches YouTube and lets you pick a result |
| `scsearch <query>` | Searches SoundCloud and lets you pick a result |
| `seek <time>` | Seeks to a position (e.g. `1:30`, `+30`, `-1:00`) |
| `shuffle` | Shuffles your tracks in the queue |
| `remove <position>` | Removes your track at the given queue position |
| `playlists` | Lists all available local playlists |
| `lyrics [song]` | Shows lyrics for the current song, or for the song you name (via [LRCLIB](https://lrclib.net)) |

### 🎚 DJ (DJ Role or Manage Server)

| Command | Description |
|---|---|
| `forceskip` | Skips immediately without a vote |
| `forceremove <@user>` | Removes all tracks queued by a user |
| `pause` | Pauses or resumes playback |
| `stop` | Stops playback, clears queue, and disconnects |
| `volume [0-150]` | Sets or shows the current volume |
| `repeat` | Cycles repeat mode: Off → All → Single |
| `skipto <position>` | Skips to a specific position in the queue |
| `movetrack <from> <to>` | Moves a track from one position to another |
| `playnext <title\|URL>` | Adds a track to the front of the queue |

### ⚙️ Admin (Manage Server)

| Command | Description |
|---|---|
| `prefix <prefix\|none>` | Sets the command prefix for this server |
| `setdj <@role\|none>` | Sets the DJ role |
| `settc <#channel\|none>` | Restricts music commands to a specific text channel |
| `setvc <channel\|none>` | Restricts the bot to a specific voice channel |
| `setskip <ratio\|none>` | Sets the vote-skip ratio (e.g. `55` or `0.55`) |
| `queuetype <fair\|linear>` | Sets the queue type for this server |

### 👑 Owner (Bot Owner Only)

| Command | Description |
|---|---|
| `autoplaylist <name\|none>` | Sets the default playlist for the current server |
| `playlist make <name>` | Creates a new empty local playlist |
| `playlist delete <name>` | Deletes a local playlist |
| `playlist append <name> <url>` | Appends a URL to a local playlist |
| `playlist write <name> <content>` | Overwrites a local playlist |
| `setavatar <url>` | Changes the bot's avatar |
| `setgame <activity>` | Changes the bot's activity status |
| `setname <name>` | Changes the bot's username |
| `setstatus <status>` | Changes the bot's online status |
| `shutdown` | Gracefully shuts down the bot |
| `debug` | Shows runtime debug information |

### ℹ️ General (Everyone)

| Command | Description |
|---|---|
| `help [command]` | Lists all commands, or shows details about one command |
| `about` | Shows information about the bot |
| `ping` | Shows the bot's latency |
| `settings` | Shows the current server settings |

---

## Project Structure

```
kmusic-bot/
├── main.py                     # Entry point
├── bot.py                      # Bot class (dependency hub)
├── config.py                   # Config loader (config.toml)
├── listeners.py                # Discord event listeners
├── config.toml.example         # Documented config template
├── requirements.txt
├── pyproject.toml              # Project metadata + pytest config
│
├── audio/
│   ├── audio_handler.py        # Per-guild player + queue management
│   ├── player_manager.py       # Lavalink node + handler registry
│   ├── nowplaying_handler.py   # Auto-refreshing NP message
│   ├── alone_in_voice_handler.py  # Auto-leave when alone
│   ├── idle_handler.py         # Auto-leave after idle timeout
│   ├── queued_track.py         # Track wrapper with requester info
│   ├── request_metadata.py     # Who requested a track
│   └── transform_source.py    # Regex URL rewriting
│
├── trackqueue/                 # (not "queue/", which would shadow Python's stdlib module)
│   ├── abstract_queue.py       # Base queue with shared operations
│   ├── fair_queue.py           # FairQueue™ interleaving algorithm
│   └── linear_queue.py         # Standard FIFO queue
│
├── settings/
│   ├── settings.py             # Per-guild settings dataclass
│   ├── settings_manager.py     # Load/save serversettings.json
│   ├── repeat_mode.py          # Enum: OFF, ALL, SINGLE
│   └── queue_type.py           # Enum: FAIR, LINEAR
│
├── commands/
│   ├── music_command.py        # Base checks (voice, text channel)
│   ├── dj_command.py           # DJ permission check
│   ├── admin_command.py        # MANAGE_GUILD check
│   ├── owner_command.py        # Bot owner check
│   ├── music/                  # 11 music commands
│   ├── dj/                     # 9 DJ commands
│   ├── admin/                  # 6 admin commands
│   ├── owner/                  # 8 owner commands
│   └── general/                # 4 general commands (incl. help)
│
├── playlist/
│   └── playlist_loader.py      # .txt playlist file management
│
├── utils/
│   ├── format_util.py          # Progress bar, volume icon, text filter
│   ├── time_util.py            # Time formatting and parsing
│   ├── other_util.py           # Activity/status parsing, version check
│   ├── lyrics_util.py          # LRCLIB lyrics search + title cleanup
│   └── prompt.py               # Interactive terminal prompts
│
├── lavalink/
│   ├── Lavalink.jar            # Download separately (not in repo)
│   └── application.yml         # Lavalink server configuration
│
├── deploy/                     # systemd user service templates
├── Playlists/                  # Local playlist .txt files (gitignored)
├── serversettings.json         # Per-guild settings (auto-created, gitignored)
└── tests/
    ├── test_fair_queue.py      # Queue logic
    ├── test_time_util.py       # Time utilities
    ├── test_lyrics_util.py     # Lyrics search helpers
    └── test_idle_handler.py    # Idle auto-leave
```

---

## Getting a Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application → go to the **Bot** tab
3. Click **Reset Token** and copy it into `config.toml`
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent** (optional, for member lookup)
5. Invite the bot to your server with these permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Add Reactions
   - Connect (voice)
   - Speak (voice)

---

## License

This project is licensed under the [Apache License 2.0](LICENSE).
