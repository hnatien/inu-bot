import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from utils import ValorantAPI
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ValorantBot')

load_dotenv()

# Fix for SSL Certificate Verification Error on macOS
import certifi
os.environ['SSL_CERT_FILE'] = certifi.where()

class ValorantBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.v_api: ValorantAPI = ValorantAPI()

    async def setup_hook(self) -> None:
        """Initialize cogs and API session"""
        await self.load_extension('cogs.stats')
        await self.load_extension('cogs.shop')
        await self.load_extension('cogs.inventory')
        await self.load_extension('cogs.info')
        
        await self.v_api.init_session()
        
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
        logger.info("Bot setup complete. Extensions loaded.")

    async def on_ready(self) -> None:
        logger.info(f'Logged in as {self.user.name if self.user else "Unknown User"}')
        await self.change_presence(activity=discord.Game(name="/help | /language vi cho Tiếng Việt!"))

    async def close(self) -> None:
        await self.v_api.close()
        await super().close()

bot = ValorantBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Centralized error handler for slash commands"""
    lang = "en"
    try:
        lang = await bot.v_api.get_language(interaction.user.id)
    except Exception:
        pass

    if isinstance(error, app_commands.CommandOnCooldown):
        from utils.i18n import t
        await interaction.response.send_message(t("error_cooldown", lang, retry_after=f"{error.retry_after:.2f}"), ephemeral=True)
    else:
        logger.error(f"App Command Error: {error}")
        from utils.i18n import t
        msg = t("error_generic", lang)
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables.")
    else:
        bot.run(token)
