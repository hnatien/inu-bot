import discord
from discord.ext import commands
from typing import Dict, Any, Union

from utils import ValorantAPI
from utils.riot_auth import AuthResult
from utils.constants import VP_ICON_URL


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

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=False)

        success, message, auth = await self.api.auth_with_url(self.url_input.value)
        if not success or not auth:
            await interaction.followup.send(f"❌ {message}")
            return

        if self.mode == "shop":
            await self._handle_shop(interaction, auth)
        else:
            await self._handle_nightmarket(interaction, auth)

    async def _handle_shop(self, interaction: discord.Interaction, auth: AuthResult) -> None:
        data = await self.api.get_shop(auth)
        if not data:
            await interaction.followup.send("❌ Không lấy được dữ liệu Daily Shop từ Riot.")
            return

        offers = data.get('SingleItemStorefrontOffers', [])
        if not offers:
            offers = data.get('SingleItemOffers', [])

        remaining = data.get('SingleItemOffersRemainingDurationInSeconds', 0)
        time_str = self._format_duration(remaining)

        header = discord.Embed(
            title="🎯 DAILY SHOP",
            description=f"Cửa hàng của **{auth.game_name}#{auth.tag_line}**\nHết hạn sau: **{time_str}**",
            color=0x2b2d31
        )
        header.set_footer(text="Inu Bot", icon_url=interaction.user.display_avatar.url)
        embeds = [header]

        for offer_id in offers:
            details = await self.api.get_skin_details(offer_id)
            if details:
                embeds.append(self._create_skin_embed(details, 0, offer_id))

        if len(embeds) <= 1:
            await interaction.followup.send("⚠️ Không tìm thấy skin nào trong Shop.")
        else:
            await interaction.followup.send(embeds=embeds)

    async def _handle_nightmarket(self, interaction: discord.Interaction, auth: AuthResult) -> None:
        data = await self.api.get_nightmarket(auth)
        if not data:
            await interaction.followup.send("❌ Hiện tại không có Night Market hoặc không lấy được dữ liệu.")
            return

        offers = data.get('BonusStoreOffers', [])
        remaining = data.get('BonusStoreRemainingDurationInSeconds', 0)
        time_str = self._format_duration(remaining)

        header = discord.Embed(
            title="🌙 NIGHT MARKET",
            description=f"Night Market của **{auth.game_name}#{auth.tag_line}**\nHết hạn sau: **{time_str}**",
            color=0x2b2d31
        )
        header.set_footer(text="Inu Bot", icon_url=interaction.user.display_avatar.url)
        embeds = [header]

        for item in offers:
            offer_id = item.get('OfferID') or item.get('Offer', {}).get('OfferID')
            if not offer_id:
                rewards = item.get('Offer', {}).get('Rewards', [])
                if rewards:
                    offer_id = rewards[0].get('ItemID')

            if not offer_id:
                continue

            discount = item.get('DiscountPercent', 0)
            details = await self.api.get_skin_details(offer_id)
            if details:
                embeds.append(self._create_skin_embed(details, discount, offer_id))

        if len(embeds) <= 1:
            await interaction.followup.send("⚠️ Không tìm thấy skin nào trong Night Market.")
        else:
            await interaction.followup.send(embeds=embeds)

    def _format_duration(self, seconds: int) -> str:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        return f"{days}d {hours}h {minutes}m" if days > 0 else f"{hours}h {minutes}m"

    def _create_skin_embed(self, details: Dict[str, Any], discount: int, offer_id: str) -> discord.Embed:
        name = details.get('name') or details.get('displayName') or 'Unknown Skin'
        icon = details.get('icon') or details.get('displayIcon')
        rarity_uuid = details.get('rarity') or details.get('contentTierUuid')
        weapon_type = details.get('weapon', "")
        is_melee = self.api.is_melee_weapon(weapon_type, name)

        base_price = self.api.get_hardcoded_price(rarity_uuid, is_melee, offer_id)
        final_price = base_price if discount == 0 else int(base_price * (100 - discount) / 100)

        rarity_info = self.api.get_rarity_info(rarity_uuid)

        # Ký tự khoảng trống braille để ép các embed cùng độ rộng
        spacer = "\u2800" * 30
        embed = discord.Embed(title=name, description=spacer, color=rarity_info['color'])
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
        self.add_item(discord.ui.Button(label="1. Đăng nhập Riot", style=discord.ButtonStyle.link, url=auth_url))

    @discord.ui.button(label="2. Dán Link vào đây", style=discord.ButtonStyle.success, emoji="📥", custom_id="shop_auth_btn")
    async def open_shop_modal(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(ShopModal(self.api, self.context, mode=self.mode))
