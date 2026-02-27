<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/discord.py-2.3+-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="discord.py">
  <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB">
  <img src="https://img.shields.io/badge/License-Personal_Use-red?style=for-the-badge" alt="License">
</p>

# 🐕 Inu Bot

A feature-rich Discord bot for tracking Valorant player statistics, daily shop rotations, and Night Market deals — powered by HenrikDev API and Riot Games OAuth2.

---

## ✨ Features

### 📊 Player Statistics
- Real-time rank, RR, and peak rank tracking
- Match history with K/D/A, ACS, and headshot percentage
- Agent and map details per match
- Player card and level display
- Global region support (auto-detected per player)

### 🔗 Account Linking
- Link your Discord account to a Riot ID for instant lookups
- Look up linked friends by mentioning them

### 🛒 Store Tracking
- Daily shop rotation viewer
- Night Market deals with discount percentages
- Skin rarity and pricing information

### 🎒 Skin Inventory
- Browse all owned weapon skins
- Filter by weapon type (Vandal, Phantom, Melee, etc.)
- Paginated display with rarity colors and icons
- Automatic deduplication of skin levels and chromas
- Multi-region support with automatic shard retry

### 🌍 Multi-Language
- Vietnamese (default) and English support
- Per-user language preference saved to database
- Switch anytime with `/language`

---

## 📋 Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Discord Bot Token](https://discord.com/developers/applications)
- [HenrikDev API Key](https://docs.henrikdev.xyz/valorant.html)
- [MongoDB Atlas](https://www.mongodb.com/atlas) (or local MongoDB instance)

---

## 🚀 Getting Started

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

Edit `.env` and fill in your actual values. See [Configuration](#-configuration) for details.

### 5. Run the bot

```bash
python main.py
```

---

## ⚙️ Configuration

| Variable | Description | Required | Default |
|---|---|---|---|
| `DISCORD_TOKEN` | Discord bot token | ✅ | — |
| `HENRIK_API_KEY` | HenrikDev API key for stats | ✅ | — |
| `MONGO_URI` | MongoDB connection string | ✅ | — |
| `RIOT_REGION` | Fallback region (`ap`, `na`, `eu`, `kr`, `latam`, `br`) | ❌ | `ap` |
| `DISCORD_WEBHOOK_URL` | Webhook URL for logging / notifications | ❌ | — |

> **Note:** Never commit your `.env` file. Use `.env.example` as a template.

---

## 💬 Commands

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

> All slash commands are also available with the `!` prefix (e.g. `!language en`).

---

## 🔐 Authentication

For `/shop`, `/nightmarket`, and `/inventory`, the bot uses Riot's official OAuth2 flow:

1. Click the **Login** button
2. Sign in on the **official Riot Games website**
3. Copy the full redirect URL
4. Paste it into the modal

**Security guarantees:**
- Users authenticate directly on Riot's official website — no passwords are collected.
- Only OAuth2 access tokens are used with **read-only** permissions.
- Tokens are held **in memory only** and discarded after the session ends.
- Sensitive data is **never** written to logs.

---

## 📁 Project Structure

```
inu-bot/
├── main.py                  # Entry point & bot setup
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── cogs/
│   ├── stats.py             # Stat, link, and unlink commands
│   ├── shop.py              # Shop and Night Market commands
│   ├── inventory.py         # Skin inventory command
│   └── info.py              # Help and update commands
├── views/
│   ├── stat_views.py        # Stat UI components & processing
│   ├── shop_views.py        # Shop UI components
│   └── inventory_views.py   # Inventory UI, weapon filter & pagination
├── utils/
│   ├── __init__.py          # ValorantAPI facade
│   ├── henrik_api.py        # HenrikDev API wrapper
│   ├── riot_auth.py         # Riot OAuth2 handler
│   ├── valorant_assets.py   # Skin & asset prefetcher
│   ├── user_manager.py      # Account linking (MongoDB)
│   ├── constants.py         # Rank tiers & icon mappings
│   └── i18n.py              # Internationalization (vi/en)
└── assets/
    └── skin_prices.json     # Skin pricing data
```

---

## 🌐 APIs Used

| API | Purpose |
|---|---|
| [HenrikDev](https://docs.henrikdev.xyz/) | Player stats, MMR, match history |
| [Valorant-API.com](https://valorant-api.com/) | Skin metadata, icons, content tiers |
| Riot Games Auth | OAuth2 authentication |
| Riot PD API | Store, Night Market, and Inventory data |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "feat: add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is for **educational and personal use only**.

Valorant and all related assets are trademarks of **Riot Games, Inc.**
This bot is not affiliated with or endorsed by Riot Games.
