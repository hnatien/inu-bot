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

class ValorantBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.v_api: ValorantAPI = ValorantAPI()

    async def setup_hook(self) -> None:
        """Initialize cogs and API session"""
        await self.load_extension('cogs.stats')
        await self.load_extension('cogs.shop')
        
        await self.v_api.init_session()
        
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
            
        logger.info("Bot setup complete. Extensions loaded.")

    async def on_ready(self) -> None:
        logger.info(f'Logged in as {self.user.name if self.user else "Unknown User"}')
        await self.change_presence(activity=discord.Game(name="/stat | /shop"))

    async def close(self) -> None:
        await self.v_api.close()
        await super().close()

bot = ValorantBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    """Centralized error handler for slash commands"""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"⌛ Lệnh đang trong thời gian chờ. Thử lại sau {error.retry_after:.2f}s.", ephemeral=True)
    else:
        logger.error(f"App Command Error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ Đã xảy ra lỗi khi thực hiện lệnh này.", ephemeral=True)
        else:
            await interaction.followup.send("❌ Đã xảy ra lỗi khi thực hiện lệnh này.", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables.")
    else:
        bot.run(token)
