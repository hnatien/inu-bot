<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-2.3+-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py">
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/License-Personal_Use-red?style=for-the-badge" alt="License">
</p>

# Inu Bot

A feature-rich Discord bot for tracking Valorant player statistics, daily shop rotations, player inventory, and Night Market deals — powered by HenrikDev API and Riot Games OAuth2.

---

## Features

### Player Statistics
- Real-time rank, RR, and peak rank tracking with visual progress bar
- Match history with K/D/A, ACS, and headshot percentage
- Agent and map details per match
- Player card and level display
- Tab-style navigation between Profile and Match History
- Global region support (auto-detected per player)

### Account Linking
- Link your Discord account to a Riot ID for instant lookups
- Look up linked friends by mentioning them

### Store Tracking
- Daily shop rotation viewer
- Night Market deals with discount percentages
- Skin rarity and pricing information
- In-place loading indicators with wait-time hints while fetching data
- Timeout-expiry notices when interactive buttons become inactive

### Skin Inventory
- Browse all owned weapon skins
- Filter by weapon type (Vandal, Phantom, Melee, etc.)
- Paginated display with rarity colors and icons
- Automatic deduplication of skin levels and chromas
- Multi-region support with automatic shard retry
- Clear error distinction between empty inventory and all-region network failures

### Multi-Language
- English (default) and Vietnamese support
- Per-user language preference saved to database
- All UI elements (buttons, embeds, errors) are fully localized
- Switch anytime with `/language`

---

## Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Discord Bot Token](https://discord.com/developers/applications)
- [HenrikDev API Key](https://docs.henrikdev.xyz/valorant.html)
- [MongoDB Atlas](https://www.mongodb.com/atlas) (or local MongoDB instance)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/hnatien/inu-bot.git
cd inu-bot
```

### 2. Create & activate a virtual environment

```bash
python -m venv venv
```

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your actual values. See [Configuration](#%EF%B8%8F-configuration) for details.

### 5. Run the bot

```bash
python main.py
```

---

## Testing

The project uses **pytest** with **pytest-asyncio** for async test support. All tests use mocks — no database, API keys, or Discord bot required.

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run a specific test file
pytest tests/test_i18n.py

# Run tests matching a pattern
pytest -k "test_iron"

# Verbose output
pytest -v

# Run with coverage
pytest --cov=utils --cov=views --cov=cogs --cov-report=term-missing
```

### Test Coverage

| Test File | Focus |
|---|---|
| `test_i18n.py` | Localization strings and fallback behavior |
| `test_constants.py` | Static data integrity |
| `test_riot_auth.py` | OAuth2 auth flow and token parsing |
| `test_henrik_api.py` | HenrikDev API wrapper and retry behavior |
| `test_valorant_assets.py` | Asset management, caching, rarity/price helpers |
| `test_user_manager.py` | MongoDB user and language operations |
| `test_facade.py` | ValorantAPI facade delegation and inventory/storefront logic |
| `test_views.py` | View helper logic |
| `test_audit_coverage.py` | Cog/view/facade behavior audit branches |
| `test_view_flows_audit.py` | End-to-end async flow simulations for stats/shop/inventory |

Current suite includes **157 tests**.

---

## Configuration

| Variable | Description | Required | Default |
|---|---|---|---|
| `DISCORD_TOKEN` | Discord bot token | Yes | — |
| `HENRIK_API_KEY` | HenrikDev API key for stats | Yes | — |
| `MONGO_URI` | MongoDB connection string | Yes | — |
| `RIOT_REGION` | Fallback region (`ap`, `na`, `eu`, `kr`, `latam`, `br`) | No | `ap` |
| `DISCORD_WEBHOOK_URL` | Webhook URL for logging / notifications | No | — |

> **Note:** Never commit your `.env` file. Use `.env.example` as a template.

---

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
| `/inventory` | Browse your owned weapon skins (requires auth) |
| `/safety` | Explains the authentication security model |
| `/language` | Switch language between Vietnamese and English |
| `/help` | Usage guide with category navigation |
| `/update` | View latest bot updates and changelog |

> All slash commands are also available with the `!` prefix (e.g. `!stat`, `!shop`, `!language en`).

---

## Authentication

For `/shop`, `/nightmarket`, and `/inventory`, the bot uses Riot's official **OAuth2 Implicit Grant** flow:

1. Click **Sign in to Riot** — you are taken to Riot's official website
2. Sign in to your Riot Games account
3. After redirect, copy the entire URL from the address bar
4. Click **Paste Link** and submit

> Buttons in auth intro views expire after 5 minutes. If expired, run the command again.

**Security guarantees:**
- Users authenticate directly on Riot's official website — no passwords are collected
- Only OAuth2 access tokens are used with **read-only** permissions
- Tokens are held **in memory only** and discarded immediately after use
- No tokens are ever written to the database or log files
- Uses the same mechanism as tracker.gg and other reputable tools

> Use `/safety` in Discord for a detailed security explanation.

---

## Architecture

Three-tier async architecture with a Facade pattern:

```
Cogs (commands) → Views (UI/embeds) → ValorantAPI Facade → Services
```

### Project Structure

```
inu-bot/
├── main.py                  # Entry point & bot setup
├── requirements.txt         # Python dependencies
├── pytest.ini               # Test configuration
├── .env.example             # Environment variable template
├── cogs/
│   ├── __init__.py           # Shared CogBase helper
│   ├── stats.py             # Stat, link, and unlink commands
│   ├── shop.py              # Shop and Night Market commands
│   ├── inventory.py         # Skin inventory command
│   └── info.py              # Help, update, and language commands
├── views/
│   ├── base_views.py        # Shared timeout + interaction UX behavior
│   ├── stat_views.py        # Stat UI (profile/match tab navigation)
│   ├── shop_views.py        # Shop UI (auth modal, skin embeds)
│   └── inventory_views.py   # Inventory UI (weapon filter, pagination)
├── utils/
│   ├── __init__.py          # ValorantAPI facade (central entry point)
│   ├── henrik_api.py        # HenrikDev API wrapper (retry, backoff)
│   ├── riot_auth.py         # Riot OAuth2 handler (AuthResult dataclass)
│   ├── valorant_assets.py   # Skin & asset prefetcher with cache
│   ├── user_manager.py      # Account linking & language prefs (MongoDB)
│   ├── constants.py         # Rank tiers, rarity data, item type IDs
│   └── i18n.py              # Internationalization (en/vi)
├── assets/
│   └── skin_prices.json     # Skin pricing overrides
└── tests/
    ├── conftest.py           # Shared fixtures (FakeSession, sample data)
    ├── test_i18n.py          # Localization tests
    ├── test_constants.py     # Static data integrity tests
    ├── test_riot_auth.py     # OAuth2 flow tests
    ├── test_henrik_api.py    # API wrapper tests
    ├── test_valorant_assets.py # Asset management tests
    ├── test_user_manager.py  # MongoDB operation tests
    ├── test_facade.py        # ValorantAPI facade tests
    ├── test_views.py         # View logic tests
    ├── test_audit_coverage.py # Cog/view/facade branch coverage tests
    └── test_view_flows_audit.py # Async flow tests for view interactions
```

### Key Design Decisions

- **Facade pattern**: `ValorantAPI` in `utils/__init__.py` composes all services — cogs never call services directly
- **Per-request auth**: `AuthResult` dataclass avoids race conditions in concurrent OAuth2 flows
- **Asset prefetching**: Weapon skins are loaded on startup via `asyncio.gather()` for instant lookups
- **Background refresh**: Asset cache refresh loop runs periodically after startup
- **In-place updates**: Bot edits the original message instead of sending new ones, reducing chat clutter
- **Timeout UX**: Shared `BaseView` disables components and notifies users when interactions expire
- **Owner-only buttons**: `interaction_check` prevents other users from clicking your buttons

---

## APIs Used

| API | Purpose |
|---|---|
| [HenrikDev](https://docs.henrikdev.xyz/) | Player stats, MMR, match history |
| [Valorant-API.com](https://valorant-api.com/) | Skin metadata, icons, content tiers |
| Riot Games Auth | OAuth2 authentication |
| Riot PD API | Store, Night Market, and Inventory data |

---

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to make sure nothing breaks (`pytest`)
4. Commit your changes (`git commit -m "feat: add amazing feature"`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## License

This project is for **educational and personal use only**.

Valorant and all related assets are trademarks of **Riot Games, Inc.**
This bot is not affiliated with or endorsed by Riot Games.
