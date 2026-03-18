# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Inu Bot is a Discord bot for tracking Valorant player statistics, daily shop rotations, skin inventory, and Night Market deals. It integrates with HenrikDev API (stats) and Riot Games OAuth2 (store/inventory).

- **Language:** Python 3.10+
- **Framework:** discord.py 2.3+ with slash commands and prefix commands
- **Database:** MongoDB via Motor (async driver)
- **Concurrency:** Fully async (aiohttp, motor, aiofiles)

## Commands

```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then fill in real values

# Run
python main.py
```

```bash
# Test
pip install pytest pytest-asyncio
pytest                    # run all tests
pytest tests/test_i18n.py # run a single test file
pytest -k "test_iron"     # run tests matching pattern
```

## Architecture

Three-tier async architecture with a Facade pattern:

```
Cogs (command handlers) → Views (UI/embeds/pagination) → ValorantAPI Facade → Services
```

**`utils/__init__.py` (ValorantAPI)** is the central facade that composes all service modules. Cogs never call services directly.

**Services:**
- `riot_auth.py` — OAuth2 flow, per-request `AuthResult` dataclass (tokens stay in memory, never persisted)
- `henrik_api.py` — HenrikDev API wrapper for stats/MMR/matches
- `valorant_assets.py` — Prefetches weapon skins on startup, caches for fast lookup
- `user_manager.py` — MongoDB ops (link/unlink accounts, language prefs)

**Cogs** (`cogs/`): `stats.py`, `shop.py`, `inventory.py`, `info.py` — each is a discord.py Cog with slash + prefix commands.

**Views** (`views/`): Discord UI components (buttons, modals, pagination). Each view file corresponds to a cog.

**i18n** (`utils/i18n.py`): Dictionary-based localization (en/vi) with `t(key, lang)` helper. All user-facing strings go here.

## Key Design Decisions

- `AuthResult` dataclass provides per-request auth context to avoid race conditions in concurrent OAuth2 flows
- Weapon skins are prefetched on startup via `ValorantAssets.fetch_all_data()` using parallel `asyncio.gather()`
- Skin inventory deduplicates chromas/levels automatically
- Region shard mapping handles Riot PD endpoint regional variants
- `constants.py` holds rank tiers, rarity data, item type IDs, and melee keywords

## Environment Variables

Required: `DISCORD_TOKEN`, `HENRIK_API_KEY`, `MONGO_URI`
Optional: `RIOT_REGION` (default: ap), `DISCORD_WEBHOOK_URL`
