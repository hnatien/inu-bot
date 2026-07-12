import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from utils import ValorantAPI
from utils.i18n import DEFAULT_LANG, t
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
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        super().__init__(command_prefix='!', intents=intents, help_command=None, proxy=proxy)
        self.v_api: ValorantAPI = ValorantAPI()

    async def setup_hook(self) -> None:
        """Initialize cogs and API session"""
        await self.load_extension('cogs.stats')
        await self.load_extension('cogs.shop')
        await self.load_extension('cogs.inventory')
        await self.load_extension('cogs.info')
        
        await self.v_api.init_session()
        asyncio.ensure_future(self.v_api._refresh_loop())

        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
        logger.info("Bot setup complete. Extensions loaded.")

    async def on_ready(self) -> None:
        logger.info(f'Logged in as {self.user.name if self.user else "Unknown User"}')
        await self.change_presence(activity=discord.Game(name="/help | /language en for English!"))

    async def close(self) -> None:
        await self.v_api.close()
        await super().close()

bot = ValorantBot()

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    """Centralized error handler for prefix commands"""
    if isinstance(error, commands.CommandOnCooldown):
        lang = DEFAULT_LANG
        try:
            lang = await bot.v_api.get_language(ctx.author.id)
        except Exception:
            pass
        await ctx.send(t("error_cooldown", lang, retry_after=f"{error.retry_after:.2f}"))
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        logger.error(f"Command Error: {error}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Centralized error handler for slash commands"""
    lang = DEFAULT_LANG
    try:
        lang = await bot.v_api.get_language(interaction.user.id)
    except Exception:
        pass

    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(t("error_cooldown", lang, retry_after=f"{error.retry_after:.2f}"), ephemeral=True)
    else:
        logger.error(f"App Command Error: {error}")
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
