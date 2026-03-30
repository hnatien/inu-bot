import discord
from discord.ext import commands
from discord import app_commands
from typing import Union
import logging

from utils import ValorantAPI
from utils.i18n import t
from views.shop_views import ShopView
from cogs import CogBase

logger = logging.getLogger('ShopCog')

class ShopCog(CogBase):
    """Cog for Valorant Shop and Night Market."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = bot.v_api

    @app_commands.command(name="shop", description="View your Daily Shop")
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
    async def shop_slash(self, interaction: discord.Interaction) -> None:
        await self._send_intro(interaction, mode="shop")

    @app_commands.command(name="nightmarket", description="View your Night Market")
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
    async def nightmarket_slash(self, interaction: discord.Interaction) -> None:
        await self._send_intro(interaction, mode="nightmarket")

    @app_commands.command(name="safety", description="Learn about the security of the Shop/Night Market feature")
    async def safety_slash(self, interaction: discord.Interaction) -> None:
        await self._send_safety_msg(interaction)

    @commands.command(name="safety")
    async def safety_prefix(self, ctx: commands.Context) -> None:
        await self._send_safety_msg(ctx)

    async def _send_safety_msg(self, context: Union[discord.Interaction, commands.Context]) -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)

        embed = discord.Embed(
            title=t("safety_title", lang),
            description=t("safety_desc", lang),
            color=0xfa4454
        )
        embed.set_footer(text=t("footer", lang))
        
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    @commands.command(name="shop")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def shop_prefix(self, ctx: commands.Context) -> None:
        await self._send_intro(ctx, mode="shop")

    @commands.command(name="nightmarket", aliases=["nm"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def nightmarket_prefix(self, ctx: commands.Context) -> None:
        await self._send_intro(ctx, mode="nightmarket")

    async def _send_intro(self, context: Union[discord.Interaction, commands.Context], mode: str = "shop") -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)

        auth_url = self.api.get_auth_link()
        view = ShopView(self.api, auth_url, context, mode=mode, lang=lang)
        
        display_mode = t("mode_daily_shop", lang) if mode == "shop" else t("mode_night_market", lang)

        embed = discord.Embed(
            title=t("title_valorant_store", lang) if mode == "shop" else t("title_night_market", lang),
            description=t("shop_intro", lang, mode=display_mode),
            color=0xfa4454
        )
        
        if isinstance(context, discord.Interaction):
            embed.set_footer(text=t("footer", lang), icon_url=context.user.display_avatar.url)
        else:
            embed.set_footer(text=t("footer", lang), icon_url=context.author.display_avatar.url)
        
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view)
            try:
                view.message = await context.original_response()
            except discord.HTTPException:
                pass
        else:
            view.message = await context.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ShopCog(bot))
