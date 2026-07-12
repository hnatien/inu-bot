# Repository Guidelines

## Project Structure & Module Organization

`main.py` starts the Discord bot and loads command extensions. Keep command handlers in `cogs/`, interactive Discord components and embeds in `views/`, and API, authentication, localization, constants, and persistence helpers in `utils/`. `utils/__init__.py` exposes the central `ValorantAPI` facade; cogs should use that facade instead of reaching into services directly. Static JSON data lives in `assets/`. Tests mirror behavior across these layers in `tests/test_*.py`.

## Build, Test, and Development Commands

- `python -m venv venv && source venv/bin/activate` creates and activates a local environment.
- `pip install -r requirements.txt` installs runtime dependencies. Install test tools separately with `pip install pytest pytest-asyncio pytest-cov`.
- `python main.py` runs the bot using values from `.env`.
- `pytest` runs the test suite; `pytest tests/test_i18n.py` or `pytest -k "fallback"` narrows the run.
- `pytest --cov=utils --cov=views --cov=cogs --cov-report=term-missing` reports coverage.
- `docker compose up --build -d` builds and starts the containerized bot; use `docker compose logs -f inu-bot` to inspect it.

## Coding Style & Naming Conventions

Target Python 3.10+ and use four-space indentation. Follow existing typed, asynchronous patterns: `snake_case` for functions and modules, `PascalCase` for classes, and uppercase names for constants. Add type hints to public boundaries and keep network/database work non-blocking. Put all user-facing English and Vietnamese strings in `utils/i18n.py`. No formatter or linter is currently configured, so keep imports, docstrings, and line wrapping consistent with neighboring code.

## Testing Guidelines

Pytest uses `asyncio_mode = auto`; async tests need no explicit event-loop setup. Name files `test_<area>.py` and tests `test_<behavior>`. Reuse fixtures and HTTP fakes from `tests/conftest.py`. Mock Discord, MongoDB, Riot, and HenrikDev boundaries—tests should not require credentials or live services. Add regression coverage for changes to commands, localization, auth/session handling, and view flows. There is no enforced coverage threshold; avoid reducing meaningful coverage.

## Commit & Pull Request Guidelines

Recent history follows Conventional Commit prefixes such as `feat:`, `fix:`, and `chore:`. Keep commits focused and use an imperative summary. Pull requests should explain the user-visible behavior, list affected commands/modules, link relevant issues, and report test commands run. Include screenshots for embed or interaction changes and call out configuration or security implications.

## Security & Configuration

Copy `.env.example` to `.env`; never commit tokens, API keys, MongoDB URIs, OAuth redirects, or backend errors. OAuth tokens must remain in memory and must not be logged or persisted. Treat changes to authentication, account linking, and `assets/users.json` as sensitive work.
