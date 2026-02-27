import asyncio
import logging
from typing import Dict, Any, Union

import discord
from discord.ext import commands

from utils import ValorantAPI
from utils.riot_auth import AuthResult
from utils.constants import VP_ICON_URL

logger = logging.getLogger('ShopViews')


class ShopModal(discord.ui.Modal):
    def __init__(self, api: ValorantAPI, context: Union[discord.Interaction, commands.Context], mode: str = "shop") -> None:
        title = 'XÁC THỰC Cửa Hàng' if mode == "shop" else 'XÁC THỰC Night Market'
        super().__init__(title=title)
        self.api = api
        self.context = context
        self.mode = mode

    url_input = discord.ui.TextInput(
        label='Dán link Redirect vào đây',
        placeholder='https://playvalorant.com/opt_in#access_token=...',
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=50
    )

    async def _resolve_region(self, auth: AuthResult) -> str:
        acc_data = await self.api.get_account_info(auth.game_name, auth.tag_line)
        if acc_data and acc_data.get('status') == 200:
            return str(acc_data.get('data', {}).get('region', '')).lower() or self.api.region
        return self.api.region

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=False)

        success, message, auth = await self.api.auth_with_url(self.url_input.value)
        if not success or not auth:
            await interaction.followup.send(f"[Error] {message}")
            return

        region = await self._resolve_region(auth)

        if self.mode == "shop":
            await self._handle_shop(interaction, auth, region)
        else:
            await self._handle_nightmarket(interaction, auth, region)

    async def _handle_shop(self, interaction: discord.Interaction, auth: AuthResult, region: str) -> None:
        data = await self.api.get_shop(auth, region=region)
        if not data:
            await interaction.followup.send("[Error] Không lấy được dữ liệu Daily Shop từ Riot.")
            return

        offers = data.get('SingleItemStorefrontOffers', [])
        if not offers:
            offers = data.get('SingleItemOffers', [])

        remaining = data.get('SingleItemOffersRemainingDurationInSeconds', 0)
        time_str = self._format_duration(remaining)

        header = discord.Embed(
            title="DAILY SHOP",
            description=f"> **Tài khoản:** `{auth.game_name}#{auth.tag_line}`\n> **Làm mới sau:** `{time_str}`",
            color=0xfa4454
        )
        header.set_footer(text="Thực hiện bởi Inu Bot", icon_url=interaction.user.display_avatar.url)
        embeds = [header]

        tasks = [self.api.get_skin_details(oid) for oid in offers]
        results = await asyncio.gather(*tasks)
        for offer_id, details in zip(offers, results):
            if details:
                embeds.append(self._create_skin_embed(details, 0, offer_id))

        if len(embeds) <= 1:
            await interaction.followup.send("[Warning] Không tìm thấy skin nào trong Shop.")
        else:
            await interaction.followup.send(embeds=embeds)

    async def _handle_nightmarket(self, interaction: discord.Interaction, auth: AuthResult, region: str) -> None:
        data = await self.api.get_nightmarket(auth, region=region)
        if not data:
            await interaction.followup.send("[Error] Hiện tại không có Night Market hoặc không lấy được dữ liệu.")
            return

        offers = data.get('BonusStoreOffers', [])
        remaining = data.get('BonusStoreRemainingDurationInSeconds', 0)
        time_str = self._format_duration(remaining)

        header = discord.Embed(
            title="NIGHT MARKET",
            description=f"> **Tài khoản:** `{auth.game_name}#{auth.tag_line}`\n> **Kết thúc sau:** `{time_str}`",
            color=0xfa4454
        )
        header.set_footer(text="Thực hiện bởi Inu Bot", icon_url=interaction.user.display_avatar.url)
        embeds = [header]

        offer_items = []
        for item in offers:
            offer_id = item.get('OfferID') or item.get('Offer', {}).get('OfferID')
            if not offer_id:
                rewards = item.get('Offer', {}).get('Rewards', [])
                if rewards:
                    offer_id = rewards[0].get('ItemID')
            if offer_id:
                offer_items.append((offer_id, item.get('DiscountPercent', 0)))

        tasks = [self.api.get_skin_details(oid) for oid, _ in offer_items]
        results = await asyncio.gather(*tasks)
        for (offer_id, discount), details in zip(offer_items, results):
            if details:
                embeds.append(self._create_skin_embed(details, discount, offer_id))

        if len(embeds) <= 1:
            await interaction.followup.send("[Warning] Không tìm thấy skin nào trong Night Market.")
        else:
            await interaction.followup.send(embeds=embeds)

    def _format_duration(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

    def _create_skin_embed(self, details: Dict[str, Any], discount: int, offer_id: str) -> discord.Embed:
        name = details.get('name') or details.get('displayName') or 'Unknown Skin'
        icon = details.get('icon') or details.get('displayIcon')
        rarity_uuid = details.get('rarity') or details.get('contentTierUuid')
        weapon_type = details.get('weapon', "")
        is_melee = self.api.is_melee_weapon(weapon_type, name)

        base_price = self.api.get_hardcoded_price(rarity_uuid, is_melee, offer_id)
        final_price = base_price if discount == 0 else int(base_price * (100 - discount) / 100)

        rarity_info = self.api.get_rarity_info(rarity_uuid)

        desc = f"**Giảm giá: {discount}%**" if discount > 0 else ""
        embed = discord.Embed(title=name, description=desc, color=rarity_info['color'])
        if icon:
            embed.set_thumbnail(url=icon)

        price_text = f"{final_price:,} VP" if final_price > 0 else "N/A"
        if discount > 0 and final_price > 0:
            price_text += f" (-{discount}%)"
            
        embed.set_footer(text=price_text, icon_url=VP_ICON_URL)
        return embed


class ShopView(discord.ui.View):
    def __init__(self, api: ValorantAPI, auth_url: str, context: Union[discord.Interaction, commands.Context], mode: str = "shop") -> None:
        super().__init__(timeout=300)
        self.api = api
        self.context = context
        self.mode = mode
        self.owner_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        
        self.add_item(discord.ui.Button(label="1. Đăng nhập Riot", style=discord.ButtonStyle.link, url=auth_url))
        
        self.auth_btn = discord.ui.Button(label="2. Dán Link vào đây", style=discord.ButtonStyle.success)
        self.auth_btn.callback = self.open_shop_modal
        self.add_item(self.auth_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("Bạn không thể sử dụng nút này.", ephemeral=True)
            return False
        return True

    async def open_shop_modal(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(ShopModal(self.api, self.context, mode=self.mode))
