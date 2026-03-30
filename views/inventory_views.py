import asyncio
import logging
import math
from typing import Dict, Any, List, Union, Optional

import discord
from discord.ext import commands

from utils import ValorantAPI
from utils.riot_auth import AuthResult
from utils.constants import INVENTORY_ITEMS_PER_PAGE, EMBED_COLOR, ERROR_COLOR
from utils.i18n import t, DEFAULT_LANG
from views.base_views import BaseView

logger = logging.getLogger('InventoryViews')

CATEGORY_EMOJIS: Dict[str, str] = {
    "skins": "🔫",
}

CATEGORY_COLORS: Dict[str, int] = {
    "skins": EMBED_COLOR,
}


class InventoryModal(discord.ui.Modal):
    def __init__(
        self,
        api: ValorantAPI,
        context: Union[discord.Interaction, commands.Context],
        lang: str = DEFAULT_LANG,
    ) -> None:
        super().__init__(title=t("inv_modal_title", lang))
        self.api = api
        self.context = context
        self.lang = lang

        self.url_input = discord.ui.TextInput(
            label=t("shop_modal_label", lang),
            placeholder="https://playvalorant.com/opt_in#access_token=...",
            style=discord.TextStyle.paragraph,
            required=True,
            min_length=50,
        )
        self.add_item(self.url_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=False)

        # Clean up intro message buttons
        if hasattr(self, 'intro_message') and self.intro_message:
            try:
                await self.intro_message.edit(view=None)
            except (discord.NotFound, discord.HTTPException):
                pass

        success, message, auth = await self.api.auth_with_url(
            self.url_input.value, lang=self.lang
        )
        if not success or not auth:
            error_embed = discord.Embed(description=message, color=ERROR_COLOR)
            await interaction.edit_original_response(embed=error_embed)
            return

        region = await self.api.resolve_region(auth)
        self.context = None

        loading_embed = discord.Embed(
            title=t("title_inventory", self.lang),
            description=(
                f"🔄 **{t('inv_loading', self.lang)}**\n"
                f"{t('shop_loading_hint', self.lang)}"
            ),
            color=EMBED_COLOR,
        )
        loading_embed.set_footer(
            text=t("footer", self.lang),
            icon_url=interaction.user.display_avatar.url,
        )
        # Update the original response instead of sending a new one
        await interaction.edit_original_response(embed=loading_embed)

        # Try multiple regions if the resolved one fails
        shards_to_try = [region, "ap", "na", "eu", "kr"]
        # Remove duplicates while preserving order
        shards_to_try = list(dict.fromkeys(shards_to_try))
        
        item_ids = []
        final_region = region
        all_failed = True
        
        for s in shards_to_try:
            logger.info(f"Trying inventory for region: {s}")
            try:
                item_ids = await asyncio.wait_for(
                    self.api.get_inventory(auth, "skins", region=s),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"Inventory request timed out for region: {s}")
                continue
            if item_ids is not None:
                all_failed = False
                final_region = s
                break

        if all_failed:
            error_embed = discord.Embed(
                title=t("title_inventory", self.lang),
                description=t("inv_error_all_regions_failed", self.lang),
                color=ERROR_COLOR,
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
            return

        if not item_ids:
            error_embed = discord.Embed(
                title=t("title_inventory", self.lang),
                description=t("inv_error_no_data", self.lang),
                color=ERROR_COLOR,
            )
            await interaction.edit_original_response(embed=error_embed, view=None)
            return

        skin_details = await self._resolve_skin_details(item_ids)

        view = InventoryPaginatorView(
            api=self.api,
            auth=auth,
            region=final_region,
            category="skins",
            items=skin_details,
            interaction=interaction,
            lang=self.lang,
        )
        embeds = view.build_page()
        await interaction.edit_original_response(embeds=embeds, view=view)
        try:
            view.message = await interaction.original_response()
        except discord.HTTPException:
            pass

    async def _resolve_skin_details(self, item_ids: List[str]) -> List[Dict[str, Any]]:
        sem = asyncio.Semaphore(10)

        async def fetch_with_limit(uid: str):
            async with sem:
                return await self.api.get_skin_details(uid)

        tasks = [fetch_with_limit(uid) for uid in item_ids]
        results = await asyncio.gather(*tasks)

        # Deduplicate by skin name to handle multiple levels/variants
        unique_skins: Dict[str, Dict[str, Any]] = {}
        for detail in results:
            if detail:
                name = detail.get("name")
                # We use the name as key. If multiple levels exist, only one is kept.
                if name and name not in unique_skins:
                    unique_skins[name] = detail
        
        resolved = list(unique_skins.values())
        resolved.sort(key=lambda d: d.get("name", ""))
        return resolved


class WeaponSelect(discord.ui.Select):
    def __init__(self, weapons: List[str], current: str, lang: str = DEFAULT_LANG) -> None:
        opts = [
            discord.SelectOption(
                label=t("inv_all_weapons", lang),
                value="All",
                emoji="🔍",
                default=(current == "All"),
            )
        ]
        for w in sorted(weapons):
            opts.append(discord.SelectOption(label=w, value=w, default=(current == w)))
        super().__init__(placeholder=t("inv_weapon_placeholder", lang), options=opts, row=0)

    async def callback(self, interaction: discord.Interaction) -> None:
        view: InventoryPaginatorView = self.view  # type: ignore[assignment]
        if interaction.user.id != view.owner_id:
            await interaction.response.send_message(
                t("button_denied", view.lang), ephemeral=True
            )
            return

        selected = self.values[0]
        if selected == view.weapon_filter:
            await interaction.response.defer()
            return

        view.weapon_filter = selected
        view.current_page = 0
        if selected == "All":
            view.items = view.all_items
        else:
            view.items = [item for item in view.all_items if item.get("weapon") == selected]
            
        view._rebuild_components()
        await interaction.response.edit_message(embeds=view.build_page(), view=view)


class InventoryPaginatorView(BaseView):
    def __init__(
        self,
        api: ValorantAPI,
        auth: AuthResult,
        region: str,
        category: str,
        items: List[Dict[str, Any]],
        interaction: discord.Interaction,
        lang: str = DEFAULT_LANG,
    ) -> None:
        super().__init__(timeout=300, lang=lang)
        self.api = api
        self.auth = auth
        self.region = region
        self.category = "skins"
        self.all_items = items
        self.items = items
        self.weapon_filter = "All"
        self.lang = lang
        self.current_page = 0
        self.owner_id = interaction.user.id
        self._avatar_url = interaction.user.display_avatar.url

        self._rebuild_components()

    @property
    def total_pages(self) -> int:
        return max(1, math.ceil(len(self.items) / INVENTORY_ITEMS_PER_PAGE))

    def _rebuild_components(self) -> None:
        self.clear_items()
        
        # Weapon filter (row 0)
        weapons = list(set([item.get("weapon", "Unknown") for item in self.all_items if item.get("weapon")]))
        weapons = [w for w in weapons if w and w != "Unknown"]
        if weapons:
            self.add_item(WeaponSelect(weapons, self.weapon_filter, self.lang))

        # Pagination (row 1)
        prev_btn = discord.ui.Button(
            emoji="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page == 0),
            row=1,
        )
        prev_btn.callback = self._prev_page
        self.add_item(prev_btn)

        page_btn = discord.ui.Button(
            label=t("inv_page", self.lang, current=self.current_page + 1, total=self.total_pages),
            style=discord.ButtonStyle.primary,
            disabled=True,
            row=1,
        )
        self.add_item(page_btn)

        next_btn = discord.ui.Button(
            emoji="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=(self.current_page >= self.total_pages - 1),
            row=1,
        )
        next_btn.callback = self._next_page
        self.add_item(next_btn)

    async def _prev_page(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                t("button_denied", self.lang), ephemeral=True
            )
            return
        self.current_page = max(0, self.current_page - 1)
        self._rebuild_components()
        await interaction.response.edit_message(embeds=self.build_page(), view=self)

    async def _next_page(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                t("button_denied", self.lang), ephemeral=True
            )
            return
        self.current_page = min(self.total_pages - 1, self.current_page + 1)
        self._rebuild_components()
        await interaction.response.edit_message(embeds=self.build_page(), view=self)

    def build_page(self) -> list:
        account = f"{self.auth.game_name}#{self.auth.tag_line}"
        category_label = t(f"inv_cat_{self.category}", self.lang)
        color = CATEGORY_COLORS.get(self.category, 0xfa4454)
        emoji = CATEGORY_EMOJIS.get(self.category, "📦")

        header = discord.Embed(
            title=f"{emoji} INVENTORY — {category_label.upper()}",
            description=t(
                "inv_header",
                self.lang,
                account=account,
                category=category_label,
                total=len(self.items),
            ),
            color=color,
        )
        header.set_footer(
            text=f"{t('footer', self.lang)} • {t('inv_page', self.lang, current=self.current_page + 1, total=self.total_pages)}",
            icon_url=self._avatar_url,
        )

        if not self.items:
            header.description = t("inv_no_items", self.lang)
            return [header]

        start = self.current_page * INVENTORY_ITEMS_PER_PAGE
        end = start + INVENTORY_ITEMS_PER_PAGE
        page_items = self.items[start:end]

        embeds = [header]

        if self.category == "skins":
            for detail in page_items:
                embeds.append(self._create_skin_embed(detail))
        else:
            desc_lines = []
            for i, item in enumerate(page_items, start=start + 1):
                name = item.get("name", "Unknown")
                desc_lines.append(f"`{i}.` {name}")

            list_embed = discord.Embed(
                description="\n".join(desc_lines),
                color=color,
            )
            embeds.append(list_embed)

        return embeds

    def _create_skin_embed(self, details: Dict[str, Any]) -> discord.Embed:
        name = details.get("name", "Unknown Skin")
        icon = details.get("icon")
        rarity_uuid = details.get("rarity")

        rarity_info = self.api.get_rarity_info(rarity_uuid)
        rarity_icon = self.api.get_rarity_icon(rarity_uuid)

        embed = discord.Embed(color=rarity_info["color"])
        if rarity_icon:
            embed.set_author(name=name, icon_url=rarity_icon)
        else:
            embed.set_author(name=name)
        if icon:
            embed.set_thumbnail(url=icon)

        tier_name = rarity_info.get("name", "")
        if tier_name and tier_name != "Unknown":
            embed.set_footer(text=tier_name)

        return embed


class InventoryIntroView(BaseView):
    def __init__(
        self,
        api: ValorantAPI,
        auth_url: str,
        context: Union[discord.Interaction, commands.Context],
        lang: str = DEFAULT_LANG,
    ) -> None:
        super().__init__(timeout=300, lang=lang)
        self.api = api
        self.context = context
        self.lang = lang
        self.owner_id = (
            context.user.id
            if isinstance(context, discord.Interaction)
            else context.author.id
        )

        self.add_item(
            discord.ui.Button(
                label=t("btn_login", lang),
                style=discord.ButtonStyle.link,
                url=auth_url,
            )
        )

        self.auth_btn = discord.ui.Button(
            label=t("btn_paste", lang), style=discord.ButtonStyle.success
        )
        self.auth_btn.callback = self._open_modal
        self.add_item(self.auth_btn)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                t("button_denied", self.lang), ephemeral=True
            )
            return False
        return True

    async def _open_modal(self, interaction: discord.Interaction) -> None:
        modal = InventoryModal(self.api, self.context, lang=self.lang)
        modal.intro_message = self.message
        await interaction.response.send_modal(modal)
