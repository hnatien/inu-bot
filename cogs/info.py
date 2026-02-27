import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, List

BOT_VERSION = "1.0.0"

EMBED_COLOR = 0xfa4454

CHANGELOG: List[dict] = [
    {
        "version": "1.0.0",
        "date": "2026-02-27",
        "changes": [
            "Ra mắt chính thức Inu Bot",
            "Tra cứu stat người chơi: rank, RR, match history",
            "Xem Daily Shop và Night Market",
            "Liên kết tài khoản Discord với Riot ID",
            "Thêm lệnh /help và /update",
        ],
    },
]

MAX_CHANGELOG_ENTRIES = 5


class HelpView(discord.ui.View):
    """Paginated help menu with category buttons."""

    def __init__(self) -> None:
        super().__init__(timeout=120)

    @discord.ui.button(label="Stat", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title="HƯỚNG DẪN — STAT",
            description=(
                "Tra cứu stat Valorant theo nhiều cách.\n\n"
                "```\n"
                "/stat              Tra cứu nhanh (nếu đã link)\n"
                "/stat user:@abc    Xem stat của người khác\n"
                "/stat name:X tag:Y Tra cứu thủ công bằng Riot ID\n"
                "```\n\n"
                "**Liên kết tài khoản**\n"
                "```\n"
                "/link name tag     Liên kết Riot ID với Discord\n"
                "/unlink            Hủy liên kết\n"
                "```\n"
                "Sau khi link, chỉ cần gõ `/stat` để xem stat ngay."
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.primary)
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title="HƯỚNG DẪN — SHOP",
            description=(
                "Xem Daily Shop và Night Market của bạn.\n\n"
                "```\n"
                "/shop              Xem Daily Shop\n"
                "/nightmarket       Xem Night Market\n"
                "/safety            Giải thích bảo mật\n"
                "```\n\n"
                "**Cách sử dụng**\n"
                "1. Gõ `/shop` hoặc `/nightmarket`\n"
                "2. Nhấn nút đăng nhập Riot\n"
                "3. Đăng nhập trên trang chính thức\n"
                "4. Copy toàn bộ URL redirect\n"
                "5. Dán link vào modal\n\n"
                "Token chỉ dùng 1 lần, không lưu trữ."
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Misc", style=discord.ButtonStyle.secondary)
    async def misc_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title="HƯỚNG DẪN — MISC",
            description=(
                "Các lệnh tiện ích khác.\n\n"
                "```\n"
                "/help              Mở menu hướng dẫn này\n"
                "/update            Xem cập nhật mới nhất\n"
                "```\n\n"
                "**Prefix**\n"
                "Tất cả lệnh đều hỗ trợ prefix `!`\n"
                "Ví dụ: `!stat`, `!shop`, `!help`\n\n"
                "**Hỗ trợ**\n"
                "Nếu gặp lỗi, hãy thử lại sau vài giây.\n"
                "Bot phụ thuộc vào API bên ngoài nên đôi khi "
                "có thể bị chậm hoặc gián đoạn."
            ),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)


def _build_help_embed() -> discord.Embed:
    embed = discord.Embed(
        title="HƯỚNG DẪN SỬ DỤNG",
        description=(
            "Inu Bot giúp bạn tra cứu stat Valorant, "
            "xem Daily Shop và Night Market.\n\n"
            "Chọn một mục bên dưới để xem chi tiết.\n\n"
            "```\n"
            "Stat        Tra cứu rank, RR, match history\n"
            "Shop        Xem shop, night market\n"
            "Misc        Prefix, hỗ trợ, cập nhật\n"
            "```"
        ),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")
    return embed


def _build_update_embed() -> discord.Embed:
    entries = CHANGELOG[:MAX_CHANGELOG_ENTRIES]
    description_parts: list[str] = []

    for entry in entries:
        changes_text = "\n".join(f"  - {c}" for c in entry["changes"])
        description_parts.append(
            f"**v{entry['version']}** — {entry['date']}\n"
            f"```\n{changes_text}\n```"
        )

    description = "\n".join(description_parts)

    embed = discord.Embed(
        title="CẬP NHẬT MỚI NHẤT",
        description=description,
        color=EMBED_COLOR,
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")
    return embed


class InfoCog(commands.Cog):
    """Cog for help and update commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _send_help(self, context: Union[discord.Interaction, commands.Context]) -> None:
        embed = _build_help_embed()
        view = HelpView()
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await context.send(embed=embed, view=view)

    async def _send_update(self, context: Union[discord.Interaction, commands.Context]) -> None:
        embed = _build_update_embed()
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    @app_commands.command(name="help", description="Hướng dẫn sử dụng Inu Bot")
    async def help_slash(self, interaction: discord.Interaction) -> None:
        await self._send_help(interaction)

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context) -> None:
        await self._send_help(ctx)

    @app_commands.command(name="update", description="Xem các cập nhật mới nhất của bot")
    async def update_slash(self, interaction: discord.Interaction) -> None:
        await self._send_update(interaction)

    @commands.command(name="update")
    async def update_prefix(self, ctx: commands.Context) -> None:
        await self._send_update(ctx)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InfoCog(bot))
