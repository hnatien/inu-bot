import discord
from discord.ext import commands
from discord import app_commands
from typing import Union
import logging

from utils import ValorantAPI
from views.shop_views import ShopView

logger = logging.getLogger('ShopCog')

class ShopCog(commands.Cog):
    """Cog for Valorant Shop and Night Market."""

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
        await self._send_safety_msg(interaction)

    @commands.command(name="safety")
    async def safety_prefix(self, ctx: commands.Context) -> None:
        await self._send_safety_msg(ctx)

    async def _send_safety_msg(self, context: Union[discord.Interaction, commands.Context]) -> None:
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
