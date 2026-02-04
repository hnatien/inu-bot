# INU-BOT

A professional Valorant tracking and utility bot for Discord.

## Features

- Real-time player statistics and rank tracking.
- Automated daily shop and Night Market monitoring.
- Recent match history analysis.
- Premium UI with Valorant-inspired aesthetics.

## Requirements

- Python 3.8 or higher.
- discord.py
- aiohttp
- python-dotenv

## Installation

1. Clone the repository to your local machine.
2. Install the necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and configure the environment variables as shown below.
4. Start the bot:
   ```bash
   python main.py
   ```

## Configuration

Required environment variables in `.env`:

- `DISCORD_TOKEN`: Your Discord Bot token.
- `HENRIK_API_KEY`: API key from HenrikDev for Valorant statistics.
- `RIOT_REGION`: The region for Riot API calls (e.g., ap, na, eu, kr).

## Architecture

- `main.py`: Entry point and bot initialization.
- `cogs/`: Modular command definitions (stats, shop).
- `utils/`: Core API wrappers and helper functions.
- `assets/`: Static resource management.

## License

This project is for educational and personal use. All game assets are property of Riot Games.
