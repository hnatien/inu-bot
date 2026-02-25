# Inu Bot

A Discord bot for tracking Valorant player statistics, daily shop, and Night Market.

## Features

**Player Statistics**
- Real-time rank, RR, and peak rank tracking
- Match history with K/D/A, ACS, and headshot percentage
- Agent and map details per match
- Player card and level display
- Global region support (auto-detected per player)

**Account Linking**
- Link your Discord account to a Riot ID for instant lookups
- Look up linked friends by mentioning them

**Store Tracking**
- Daily shop rotation viewer
- Night Market deals with discount percentages
- Skin rarity and pricing information

## Prerequisites

- Python 3.10+
- [Discord Bot Token](https://discord.com/developers/applications)
- [HenrikDev API Key](https://docs.henrikdev.xyz/valorant.html)

## Installation

```bash
git clone https://github.com/hnatien/inu-bot.git
cd inu-bot
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token
HENRIK_API_KEY=your_henrikdev_api_key
RIOT_REGION=ap
```

Run the bot:

```bash
python main.py
```

## Configuration

| Variable | Description | Required | Default |
|---|---|---|---|
| `DISCORD_TOKEN` | Discord bot token | Yes | - |
| `HENRIK_API_KEY` | HenrikDev API key | Yes | - |
| `RIOT_REGION` | Fallback region (`ap`, `na`, `eu`, `kr`, `latam`, `br`) | No | `ap` |

## Commands

| Command | Description |
|---|---|
| `/stat` | Look up your stats (if linked) or open manual search |
| `/stat user:@member` | Look up a linked member's stats |
| `/stat name:Riot tag:ID` | Look up any player by Riot ID |
| `/link name tag` | Link your Discord to a Riot ID |
| `/unlink` | Remove your linked account |
| `/shop` | View your daily shop (requires auth) |
| `/nightmarket` | View Night Market deals (requires auth) |
| `/safety` | Explains the authentication security model |

All slash commands are also available with the `!` prefix.

## Authentication

For `/shop` and `/nightmarket`:

1. Click the login button
2. Sign in on the official Riot Games website
3. Copy the full redirect URL
4. Paste it into the modal

Tokens are read-only, held in memory only, and discarded after the session ends.

## Project Structure

```
inu-bot/
├── main.py                  # Entry point
├── requirements.txt
├── .env
├── cogs/
│   ├── stats.py             # Stat, link, and unlink commands
│   └── shop.py              # Shop and Night Market commands
├── views/
│   ├── stat_views.py        # Stat UI components and processing
│   └── shop_views.py        # Shop UI components
├── utils/
│   ├── __init__.py          # ValorantAPI facade
│   ├── henrik_api.py        # HenrikDev API wrapper
│   ├── riot_auth.py         # Riot OAuth2 handler
│   ├── valorant_assets.py   # Skin and asset fetcher
│   ├── user_manager.py      # Account linking persistence
│   └── constants.py         # Rank tiers and icon mappings
└── assets/
    └── skin_prices.json     # Hardcoded skin pricing data
```

## APIs

| API | Purpose |
|---|---|
| [HenrikDev](https://docs.henrikdev.xyz/) | Player stats, MMR, match history |
| [Valorant-API.com](https://valorant-api.com/) | Skin metadata, icons, content tiers |
| Riot Games Auth | OAuth2 authentication |
| Riot PD API | Store and Night Market data |

## Security

- Users authenticate directly on Riot's official website. No passwords are collected.
- Only OAuth2 access tokens are used with read-only permissions.
- Tokens are held in memory and discarded after use.
- Sensitive data is never written to logs.

## License

This project is for educational and personal use only. Valorant and all related assets are trademarks of Riot Games, Inc.

This bot is not affiliated with or endorsed by Riot Games.
