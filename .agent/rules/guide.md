---
trigger: always_on
---

# PYTHON DISCORD BOT DEVELOPMENT STANDARDS

## 1. STRUCTURE
- Use Cogs for modularity.
- Root: `main.py`, `.env`, `.gitignore`.
- Directories: `/cogs`, `/utils`, `/assets`.
- Logic: Separate API wrappers from command definitions.

## 2. ASYNC & I/O
- Forbidden: `requests`, `time.sleep`, `open()` (synchronous).
- Required: `aiohttp`, `asyncio.sleep()`, `aiofiles`.
- Implement `interaction.response.defer()` for tasks > 2s.

## 3. UI/UX (VALORANT STYLE)
- Use `discord.app_commands` (Slash Commands).
- Display: `discord.Embed` + `discord.ui.View`.
- Formatting: Monospace code blocks for alignment.
- Interaction: Use Buttons/Select Menus for navigation.

## 4. CODE QUALITY
- Follow PEP 8 (naming, spacing).
- Mandatory Type Hinting for all parameters and returns.
- Minimal comments: Code must be self-explanatory.
- Centralized error handling via `on_app_command_error`.

## 5. SECURITY
- Zero hardcoded secrets; use `os.getenv`.
- Encrypt sensitive user data at rest.
- Strict adherence to Riot/Discord rate limits.