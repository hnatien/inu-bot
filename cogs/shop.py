import discord
from discord.ext import commands
from discord import app_commands
from utils.riot_api import ValorantAPI
import asyncio
from typing import Optional, List, Dict, Any, Union

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
        
        success, message = await self.api.auth_with_url(self.url_input.value)
        if not success:
            await interaction.followup.send(f"❌ {message}")
            return

        if self.mode == "shop":
            await self._handle_shop(interaction)
        else:
            await self._handle_nightmarket(interaction)

    async def _handle_shop(self, interaction: discord.Interaction) -> None:
        data = await self.api.get_shop()
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
            description=f"Cửa hàng của **{self.api.game_name}#{self.api.tag_line}**\nHết hạn sau: **{time_str}**",
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

    async def _handle_nightmarket(self, interaction: discord.Interaction) -> None:
        data = await self.api.get_nightmarket()
        if not data:
            await interaction.followup.send("❌ Hiện tại không có Night Market hoặc không lấy được dữ liệu.")
            return

        offers = data.get('BonusStoreOffers', [])
        remaining = data.get('BonusStoreRemainingDurationInSeconds', 0)
        time_str = self._format_duration(remaining)

        header = discord.Embed(
            title="🌙 NIGHT MARKET",
            description=f"Night Market của **{self.api.game_name}#{self.api.tag_line}**\nHết hạn sau: **{time_str}**",
            color=0x2b2d31
        )
        header.set_footer(text="Inu Bot", icon_url=interaction.user.display_avatar.url)
        embeds = [header]

        for item in offers:
            offer_id = item.get('OfferID') or item.get('Offer', {}).get('OfferID')
            if not offer_id:
                rewards = item.get('Offer', {}).get('Rewards', [])
                if rewards: offer_id = rewards[0].get('ItemID')
            
            if not offer_id: continue

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
        
        is_melee = weapon_type.lower() == "melee" or any(k in name.lower() for k in ["knife", "karambit", "butterfly", "axe", "blade", "hammer", "dagger", "fan", "bat", "scythe", "gauntlet", "stiletto", "crowbar"])

        base_price = self.api.get_hardcoded_price(rarity_uuid, is_melee, offer_id)
        final_price = base_price if discount == 0 else int(base_price * (100 - discount) / 100)
        
        rarity_info = self.api.get_rarity_info(rarity_uuid)
        
        desc = f"**🔥 Giảm giá: {discount}%**" if discount > 0 else ""
        embed = discord.Embed(title=name, description=desc, color=rarity_info['color'])
        if icon: embed.set_thumbnail(url=icon)
        
        price_text = f"{final_price:,} VP" if final_price > 0 else "N/A"
        embed.set_footer(text=price_text, icon_url=self.api.VP_ICON_URL)
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

class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = getattr(bot, 'v_api')

    @app_commands.command(name="shop", description="Xem Daily Shop của bạn")
    async def shop_slash(self, interaction: discord.Interaction) -> None:
        await self._send_intro(interaction, mode="shop")

    @app_commands.command(name="nightmarket", description="Xem Night Market của bạn")
    async def nightmarket_slash(self, interaction: discord.Interaction) -> None:
        await self._send_intro(interaction, mode="nightmarket")

    @app_commands.command(name="safety", description="Giải thích về tính an toàn khi sử dụng tính năng Shop/Night Market")
    async def safety_slash(self, interaction: discord.Interaction) -> None:
        """Giải thích cơ chế bảo mật của Token Authentication"""
        await self._send_safety_msg(interaction)

    @commands.command(name="safety")
    async def safety_prefix(self, ctx: commands.Context) -> None:
        """Phiên bản lệnh prefix của safety"""
        await self._send_safety_msg(ctx)

    async def _send_safety_msg(self, context: Union[discord.Interaction, commands.Context]) -> None:
        """Hàm dùng chung để gửi nội dung giải thích bảo mật"""
        description = (
            "Hệ thống sử dụng cơ chế **OAuth2 Implicit Grant** của Riot Games, tương tự như cách các trang web như "
            "tracker.gg hay các ứng dụng mã nguồn mở uy tín đang hoạt động.\n\n"
            "**Tại sao phương thức này an toàn?**\n"
            "1. **Không yêu cầu Mật khẩu:** Bạn đăng nhập trực tiếp trên trang chủ `auth.riotgames.com`. Bot hoàn toàn không can thiệp vào quá trình này.\n"
            "2. **Cơ chế Token:** Link bạn cung cấp chỉ chứa *Access Token* - một dạng 'mã định danh tạm thời'. Nó chỉ có quyền đọc dữ liệu cửa hàng và MMR, không thể đổi mật khẩu hay thực hiện giao dịch.\n"
            "3. **Không lưu trữ:** Bot chỉ sử dụng Token trong bộ nhớ tạm (RAM) để truy vấn API và sẽ bị xóa ngay sau khi phiên làm việc kết thúc.\n"
            "4. **Zero Logs:** Chúng tôi cam kết không ghi nhận (log) bất kỳ Token nào vào cơ sở dữ liệu.\n\n"
            "*Khuyến cáo: Luôn sử dụng xác thực 2 lớp (2FA) cho tài khoản Riot của bạn để đảm bảo an toàn tối đa.*"
        )
        
        embed = discord.Embed(
            title="GIẢI THÍCH VỀ BẢO MẬT",
            description=description,
            color=0x2b2d31
        )
        embed.set_footer(text="Inu Bot")
        
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    @commands.command(name="shop")
    async def shop_prefix(self, ctx: commands.Context) -> None:
        await self._send_intro(ctx, mode="shop")

    @commands.command(name="nightmarket", aliases=["nm"])
    async def nightmarket_prefix(self, ctx: commands.Context) -> None:
        await self._send_intro(ctx, mode="nightmarket")

    async def _send_intro(self, context: Union[discord.Interaction, commands.Context], mode: str = "shop") -> None:
        auth_url = self.api.get_auth_link()
        view = ShopView(self.api, auth_url, context, mode=mode)
        
        display_mode = "Daily Shop" if mode == "shop" else "Night Market"
        title = "🛒 VALORANT STORE" if mode == "shop" else "🌙 NIGHT MARKET"
        description = (
            f"Để xem **{display_mode}**, vui lòng làm theo các bước:\n\n"
            "1. Nhấn **Đăng nhập Riot** và đăng nhập tài khoản của bạn.\n"
            "2. Sau khi hiện trang trắng (hoặc lỗi), **Copy toàn bộ Link** trên thanh địa chỉ.\n"
            "3. Nhấn **Dán Link vào đây** và gửi link bạn vừa copy."
        )
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=0x2b2d31
        )
        embed.set_footer(text="Inu Bot")
        
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view)
        else:
            await context.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ShopCog(bot))
