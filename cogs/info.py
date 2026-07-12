import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union, List

from utils import ValorantAPI
from utils.i18n import DEFAULT_LANG, t
from cogs import CogBase
from views.base_views import BaseView

BOT_VERSION = "1.2.0"

CHANGELOG: List[dict] = [
    {
        "version": "1.2.0",
        "date": "2026-07-12",
        "changes_vi": [
            "Thiết kế lại /help theo hướng đơn giản, dễ tra cứu",
            "Làm mới giao diện Daily Shop và quy trình đăng nhập Riot",
            "Chuẩn hóa các màn loading, loại bỏ chi tiết dư thừa",
            "Cải thiện bố cục hồ sơ rank và lịch sử trận đấu",
            "Bỏ màu embed trên các màn, trừ màu rank trong Stat",
        ],
        "changes_en": [
            "Redesigned /help for simpler navigation",
            "Refined the Daily Shop UI and Riot sign-in flow",
            "Standardized loading screens and removed visual clutter",
            "Improved rank profile and match history layouts",
            "Removed embed colors except rank colors in Stats",
        ],
    },
    {
        "version": "1.1.0",
        "date": "2026-02-27",
        "changes_vi": [
            "Thêm tính năng Inventory: Xem kho đồ skin súng",
            "Hỗ trợ lọc theo loại súng (Vandal, Phantom, v.v.)",
            "Sửa lỗi ảnh skin bị zoom/crop (Prime, Sovereign...)",
            "Tự động gộp skin level và chroma để kho đồ gọn gàng hơn",
            "Hệ thống Multi-Region retry (tự động thử các vùng AP, NA, EU, KR)",
        ],
        "changes_en": [
            "Added Inventory feature: Browse your weapon skins",
            "Support filtering by weapon type (Vandal, Phantom, etc.)",
            "Fixed skin image crops/zooms (Prime, Sovereign, etc.)",
            "Auto-deduplicate skin levels and chromas for a cleaner list",
            "Multi-Region retry system (automatically tries AP, NA, EU, KR)",
        ],
    },
    {
        "version": "1.0.0",
        "date": "2026-02-27",
        "changes_vi": [
            "Ra mắt Inu Bot",
            "Tra cứu stat: rank, RR, lịch sử trận đấu",
            "Xem Daily Shop và Night Market",
            "Liên kết tài khoản Discord với Riot ID",
            "Thêm lệnh /help và /update",
        ],
        "changes_en": [
            "Official launch of Inu Bot",
            "Player stat lookup: rank, RR, match history",
            "View Daily Shop and Night Market",
            "Link Discord account to Riot ID",
            "Added /help and /update commands",
        ],
    },
]

MAX_CHANGELOG_ENTRIES = 5

SUPPORTED_LANGS = [
    app_commands.Choice(name="Tiếng Việt", value="vi"),
    app_commands.Choice(name="English", value="en"),
]


class HelpView(BaseView):
    """Category navigation for the help menu."""

    def __init__(self, lang: str = DEFAULT_LANG, owner_id: int = 0) -> None:
        super().__init__(timeout=120, lang=lang)
        self.lang = lang
        self.owner_id = owner_id
        labels = {
            "help:stat": t("help_stat_label", lang),
            "help:shop": t("help_shop_label", lang),
            "help:inventory": t("help_inv_label", lang),
            "help:misc": t("help_misc_label", lang),
        }
        for item in self.children:
            if isinstance(item, discord.ui.Button) and item.custom_id in labels:
                item.label = labels[item.custom_id]

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if self.owner_id and interaction.user.id != self.owner_id:
            await interaction.response.send_message(t("button_denied", self.lang), ephemeral=True)
            return False
        return True

    @discord.ui.button(
        label="Stat",
        style=discord.ButtonStyle.secondary,
        custom_id="help:stat",
        row=0
    )
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_stat_title", self.lang),
            description=t("help_stat_desc", self.lang),
        )
        embed.set_footer(text=t("footer", self.lang))
        self._set_active_button("help:stat")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Shop",
        style=discord.ButtonStyle.secondary,
        custom_id="help:shop",
        row=0
    )
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_shop_title", self.lang),
            description=t("help_shop_desc", self.lang),
        )
        embed.set_footer(text=t("footer", self.lang))
        self._set_active_button("help:shop")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Inventory",
        style=discord.ButtonStyle.secondary,
        custom_id="help:inventory",
        row=0
    )
    async def inventory_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_inv_title", self.lang),
            description=t("help_inv_desc", self.lang),
        )
        embed.set_footer(text=t("footer", self.lang))
        self._set_active_button("help:inventory")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Misc",
        style=discord.ButtonStyle.secondary,
        custom_id="help:misc",
        row=0
    )
    async def misc_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_misc_title", self.lang),
            description=t("help_misc_desc", self.lang),
        )
        embed.set_footer(text=t("footer", self.lang))
        self._set_active_button("help:misc")
        await interaction.response.edit_message(embed=embed, view=self)

    def _set_active_button(self, custom_id: str) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.style = (
                    discord.ButtonStyle.primary
                    if item.custom_id == custom_id
                    else discord.ButtonStyle.secondary
                )


def _build_help_embed(lang: str = DEFAULT_LANG, bot: Optional[commands.Bot] = None) -> discord.Embed:
    embed = discord.Embed(
        title=t("help_title", lang),
        description=t("help_desc", lang),
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")

    embed.add_field(name=t('help_stat_label', lang), value=t('help_stat_sub', lang), inline=False)
    embed.add_field(name=t('help_shop_label', lang), value=t('help_shop_sub', lang), inline=False)
    embed.add_field(name=t('help_inv_label', lang), value=t('help_inv_sub', lang), inline=False)
    embed.add_field(name=t('help_misc_label', lang), value=t('help_misc_sub', lang), inline=False)

    return embed


def _build_update_embed(lang: str = DEFAULT_LANG) -> discord.Embed:
    entries = CHANGELOG[:MAX_CHANGELOG_ENTRIES]
    description_parts: list[str] = []

    for entry in entries:
        changes = entry.get(f"changes_{lang}", entry.get("changes_en"))
        changes_text = "\n".join(f"  - {c}" for c in changes)
        description_parts.append(
            f"**v{entry['version']}** — {entry['date']}\n"
            f"```\n{changes_text}\n```"
        )

    description = "\n".join(description_parts)

    embed = discord.Embed(
        title=t("update_title", lang),
        description=description,
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")
    return embed


class InfoCog(CogBase):
    """Cog for help, update, and language commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = bot.v_api

    async def _send_help(self, context: Union[discord.Interaction, commands.Context]) -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)
        embed = _build_help_embed(lang, self.bot)
        view = HelpView(lang, owner_id=user_id)
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view, ephemeral=True)
            try:
                view.message = await context.original_response()
            except discord.HTTPException:
                pass
        else:
            view.message = await context.send(embed=embed, view=view)

    async def _send_update(self, context: Union[discord.Interaction, commands.Context]) -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)
        embed = _build_update_embed(lang)
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, ephemeral=True)
        else:
            await context.send(embed=embed)

    @app_commands.command(name="help", description="How to use Inu Bot")
    async def help_slash(self, interaction: discord.Interaction) -> None:
        await self._send_help(interaction)

    @commands.command(name="help")
    async def help_prefix(self, ctx: commands.Context) -> None:
        await self._send_help(ctx)

    @app_commands.command(name="update", description="View the latest bot updates")
    async def update_slash(self, interaction: discord.Interaction) -> None:
        await self._send_update(interaction)

    @commands.command(name="update")
    async def update_prefix(self, ctx: commands.Context) -> None:
        await self._send_update(ctx)

    @app_commands.command(name="language", description="Change the bot language / Đổi ngôn ngữ")
    @app_commands.describe(lang="Choose your language / Chọn ngôn ngữ")
    @app_commands.choices(lang=SUPPORTED_LANGS)
    async def language_slash(self, interaction: discord.Interaction, lang: app_commands.Choice[str]) -> None:
        await self.api.set_language(interaction.user.id, lang.value)
        await interaction.response.send_message(t("lang_set", lang.value), ephemeral=True)

    @commands.command(name="language", aliases=["lang"])
    async def language_prefix(self, ctx: commands.Context, lang: str = "") -> None:
        lang = lang.strip().lower()
        if lang not in ("vi", "en"):
            await ctx.send("Usage: `!language vi` or `!language en`")
            return
        await self.api.set_language(ctx.author.id, lang)
        await ctx.send(t("lang_set", lang))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(InfoCog(bot))
