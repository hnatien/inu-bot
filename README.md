# Inu Bot

A Discord bot for tracking Valorant player statistics, daily shop, and Night Market.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Security](#security)
- [License](#license)

## Features

**Player Statistics**
- Real-time rank and RR (Rating Points) tracking
- Match history with K/D/A and ACS metrics
- Player card and level display

**Store Tracking**
- Daily Shop rotation viewer
- Night Market deals with discount percentages
- Skin rarity and pricing information

## Prerequisites

- Python 3.10 or higher
- Discord Bot Token ([Discord Developer Portal](https://discord.com/developers/applications))
- HenrikDev API Key ([HenrikDev](https://docs.henrikdev.xyz/valorant.html))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/inu-bot.git
   cd inu-bot
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```env
   DISCORD_TOKEN=your_discord_bot_token
   HENRIK_API_KEY=your_henrikdev_api_key
   RIOT_REGION=ap
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Configuration

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_TOKEN` | Discord Bot token | Yes | - |
| `HENRIK_API_KEY` | HenrikDev API key for stats | Yes | - |
| `RIOT_REGION` | Riot API region (`ap`, `na`, `eu`, `kr`, `latam`, `br`) | No | `ap` |

## Usage

### Slash Commands

| Command | Description |
|---------|-------------|
| `/stat` | Look up player statistics by Riot ID |
| `/shop` | View your Daily Shop (requires authentication) |
| `/nightmarket` | View your Night Market deals (requires authentication) |
| `/safety` | Explains the security of the authentication process |

### Prefix Commands

All slash commands are also available with the `!` prefix (e.g., `!stat`, `!shop`).

### Authentication Flow

For `/shop` and `/nightmarket` commands:

1. Click the **Login to Riot** button
2. Sign in on the official Riot Games website
3. Copy the full redirect URL (starts with `https://playvalorant.com/opt_in#access_token=...`)
4. Paste the URL into the modal

The bot uses OAuth2 tokens which are:
- Read-only (cannot make purchases or change settings)
- Not stored permanently
- Discarded after the session ends

## Project Structure

```
inu-bot/
├── main.py              # Bot entry point and initialization
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
├── cogs/
│   ├── shop.py          # Shop and Night Market commands
│   └── stats.py         # Player statistics commands
├── utils/
│   └── riot_api.py      # Riot and HenrikDev API wrapper
└── assets/
    └── skin_prices.json # Hardcoded skin pricing data
```

## API Reference

This bot integrates with the following APIs:

| API | Purpose | Documentation |
|-----|---------|---------------|
| Riot Games Auth | OAuth2 authentication | [Riot Developer Portal](https://developer.riotgames.com/) |
| Riot PD API | Store/Night Market data | Internal API |
| HenrikDev API | Player stats, MMR, match history | [HenrikDev Docs](https://docs.henrikdev.xyz/) |
| Valorant-API.com | Skin metadata, icons, content tiers | [Valorant-API](https://valorant-api.com/) |

## Security

- **No password collection**: Users authenticate directly on Riot's official website
- **Token-based access**: Only OAuth2 access tokens are used, which have limited read-only permissions
- **No persistent storage**: Tokens are held in memory only and discarded after use
- **Sanitized logging**: Sensitive data is never written to logs

For detailed security information, use the `/safety` command.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is for educational and personal use only. Valorant and all related assets are trademarks of Riot Games, Inc.

---

**Disclaimer**: This bot is not affiliated with or endorsed by Riot Games.
