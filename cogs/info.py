import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, List

from utils import ValorantAPI
from utils.i18n import t

BOT_VERSION = "1.0.0"

EMBED_COLOR = 0xfa4454

CHANGELOG: List[dict] = [
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


class HelpView(discord.ui.View):
    """Paginated help menu with category buttons."""

    def __init__(self, lang: str = "vi") -> None:
        super().__init__(timeout=120)
        self.lang = lang

    @discord.ui.button(label="Stat", style=discord.ButtonStyle.primary)
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_stat_title", self.lang),
            description=t("help_stat_desc", self.lang),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Shop", style=discord.ButtonStyle.primary)
    async def shop_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_shop_title", self.lang),
            description=t("help_shop_desc", self.lang),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Misc", style=discord.ButtonStyle.secondary)
    async def misc_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = discord.Embed(
            title=t("help_misc_title", self.lang),
            description=t("help_misc_desc", self.lang),
            color=EMBED_COLOR,
        )
        embed.set_footer(text="Inu Bot")
        await interaction.response.edit_message(embed=embed, view=self)


def _build_help_embed(lang: str = "vi") -> discord.Embed:
    embed = discord.Embed(
        title=t("help_title", lang),
        description=t("help_desc", lang),
        color=EMBED_COLOR,
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")
    return embed


def _build_update_embed(lang: str = "vi") -> discord.Embed:
    entries = CHANGELOG[:MAX_CHANGELOG_ENTRIES]
    description_parts: list[str] = []

    for entry in entries:
        changes = entry.get(f"changes_{lang}", entry.get("changes_vi"))
        changes_text = "\n".join(f"  - {c}" for c in changes)
        description_parts.append(
            f"**v{entry['version']}** — {entry['date']}\n"
            f"```\n{changes_text}\n```"
        )

    description = "\n".join(description_parts)

    embed = discord.Embed(
        title=t("update_title", lang),
        description=description,
        color=EMBED_COLOR,
    )
    embed.set_footer(text=f"Inu Bot v{BOT_VERSION}")
    return embed


class InfoCog(commands.Cog):
    """Cog for help, update, and language commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = getattr(bot, 'v_api')

    async def _get_lang(self, user_id: int) -> str:
        return await self.api.get_language(user_id)

    async def _send_help(self, context: Union[discord.Interaction, commands.Context]) -> None:
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        lang = await self._get_lang(user_id)
        embed = _build_help_embed(lang)
        view = HelpView(lang)
        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await context.send(embed=embed, view=view)

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
