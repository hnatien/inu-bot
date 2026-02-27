import discord
from discord.ext import commands
from discord import app_commands
from typing import Union
import logging

from utils import ValorantAPI
from utils.i18n import t
from views.inventory_views import InventoryIntroView

logger = logging.getLogger('InventoryCog')


class InventoryCog(commands.Cog):
    """Cog for viewing player's Valorant inventory (owned skins, agents, etc.)."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = getattr(bot, 'v_api')

    async def _get_lang(self, user_id: int) -> str:
        return await self.api.get_language(user_id)

    @app_commands.command(name="inventory", description="View your Valorant Inventory")
    async def inventory_slash(self, interaction: discord.Interaction) -> None:
        await self._send_intro(interaction)

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory_prefix(self, ctx: commands.Context) -> None:
        await self._send_intro(ctx)

    async def _send_intro(self, context: Union[discord.Interaction, commands.Context]) -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)

        auth_url = self.api.get_auth_link()
        view = InventoryIntroView(self.api, auth_url, context, lang=lang)

        embed = discord.Embed(
            title="VALORANT INVENTORY",
            description=t("inv_intro", lang),
            color=0xfa4454,
        )

        if isinstance(context, discord.Interaction):
            embed.set_footer(text=t("footer", lang), icon_url=context.user.display_avatar.url)
            await context.response.send_message(embed=embed, view=view)
        else:
            embed.set_footer(text=t("footer", lang), icon_url=context.author.display_avatar.url)
            await context.send(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InventoryCog(bot))
