"""Flow-level tests for heavily asynchronous view and stats command logic."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from cogs.stats import StatsCog
from views.inventory_views import InventoryModal, InventoryPaginatorView
from views.shop_views import ShopModal
from views.stat_views import PlayerStatsPagination, StatModal, StatView, process_and_send_stats


class DummyInteraction:
    def __init__(self, user_id: int = 1, response_done: bool = False):
        self.user = SimpleNamespace(
            id=user_id,
            display_avatar=SimpleNamespace(url="https://avatar.example/u.png"),
            display_name=f"u{user_id}",
        )
        self.response = SimpleNamespace(
            send_message=AsyncMock(),
            edit_message=AsyncMock(),
            defer=AsyncMock(),
            send_modal=AsyncMock(),
            is_done=MagicMock(return_value=response_done),
        )
        self.followup = SimpleNamespace(send=AsyncMock())
        self.edit_original_response = AsyncMock()
        self.original_response = AsyncMock(return_value=SimpleNamespace(edit=AsyncMock(), reply=AsyncMock()))


class DummyContext:
    def __init__(self, user_id: int = 1):
        self.author = SimpleNamespace(
            id=user_id,
            display_avatar=SimpleNamespace(url="https://avatar.example/a.png"),
            display_name=f"a{user_id}",
        )
        self.send = AsyncMock(return_value=SimpleNamespace(edit=AsyncMock(), reply=AsyncMock()))


@pytest.fixture
def api_mock():
    api = MagicMock()
    api.get_rank_assets.return_value = (0x123456, "https://rank.icon")
    api.get_rarity_info.return_value = {"name": "Premium", "color": 0x999999}
    api.get_rarity_icon.return_value = "https://rarity.icon"
    api.get_hardcoded_price.return_value = 1775
    api.is_melee_weapon.return_value = False
    return api


class TestStatViewFlows:
    async def test_process_stats_success_interaction(self, api_mock, monkeypatch):
        monkeypatch.setattr("views.stat_views.discord.Interaction", DummyInteraction)
        api_mock.get_account_info = AsyncMock(return_value={
            "status": 200,
            "data": {
                "region": "ap",
                "account_level": 100,
                "card": {"small": "https://card.s", "large": "https://card.l"},
            },
        })
        api_mock.get_stats = AsyncMock(return_value={
            "status": 200,
            "data": {
                "current": {"tier": {"name": "Gold 2"}, "rr": 67},
                "peak": {"tier": {"name": "Platinum 1"}},
            },
        })
        api_mock.get_recent_matches = AsyncMock(return_value={
            "status": 200,
            "data": [{
                "metadata": {"mode": "Competitive", "map": "Ascent", "rounds_played": 24},
                "players": {"all_players": [{
                    "name": "TenZ", "tag": "SEN", "team": "blue", "character": "Jett",
                    "stats": {
                        "kills": 20, "deaths": 10, "assists": 5, "score": 5000,
                        "headshots": 10, "bodyshots": 20, "legshots": 5,
                    },
                }]},
                "teams": {"blue": {"has_won": True}},
            }],
        })

        interaction = DummyInteraction(user_id=10)
        await process_and_send_stats(interaction, api_mock, "TenZ", "SEN", lang="en")

        interaction.response.defer.assert_awaited_once()
        assert interaction.edit_original_response.await_count >= 2

    async def test_process_stats_account_error(self, api_mock, monkeypatch):
        monkeypatch.setattr("views.stat_views.discord.Interaction", DummyInteraction)
        api_mock.get_account_info = AsyncMock(return_value={"status": 404, "message": "not found"})
        interaction = DummyInteraction(user_id=10)
        await process_and_send_stats(interaction, api_mock, "Bad", "TAG", lang="en")
        interaction.edit_original_response.assert_awaited()

    async def test_process_stats_rank_error(self, api_mock, monkeypatch):
        monkeypatch.setattr("views.stat_views.discord.Interaction", DummyInteraction)
        api_mock.get_account_info = AsyncMock(return_value={
            "status": 200,
            "data": {"region": "ap", "account_level": 1, "card": {}},
        })
        api_mock.get_stats = AsyncMock(return_value={"status": 500, "message": "rank fail"})
        api_mock.get_recent_matches = AsyncMock(return_value={"status": 200, "data": []})
        interaction = DummyInteraction(user_id=10)
        await process_and_send_stats(interaction, api_mock, "TenZ", "SEN", lang="en")
        interaction.edit_original_response.assert_awaited()


class TestShopViewFlows:
    async def test_shop_modal_submit_auth_fail_and_success(self, api_mock):
        context = DummyInteraction(user_id=9)
        modal = ShopModal(api_mock, context, mode="shop", lang="en")
        modal.url_input._value = "https://playvalorant.com/opt_in#access_token=x"
        interaction = DummyInteraction(user_id=9)

        api_mock.auth_with_url = AsyncMock(return_value=(False, "bad", None))
        await modal.on_submit(interaction)
        interaction.edit_original_response.assert_awaited()

        api_mock.auth_with_url = AsyncMock(return_value=(True, "ok", SimpleNamespace(game_name="TenZ", tag_line="SEN", puuid="p", headers={})))
        api_mock.resolve_region = AsyncMock(return_value="ap")
        modal._handle_shop = AsyncMock()
        await modal.on_submit(interaction)
        modal._handle_shop.assert_awaited_once()

    async def test_handle_shop_success_and_no_data(self, api_mock):
        modal = ShopModal.__new__(ShopModal)
        modal.api = api_mock
        modal.lang = "en"
        interaction = DummyInteraction(user_id=1)
        auth = SimpleNamespace(game_name="TenZ", tag_line="SEN")

        api_mock.get_shop = AsyncMock(return_value={
            "SingleItemOffers": ["offer-1"],
            "SingleItemOffersRemainingDurationInSeconds": 3600,
        })
        api_mock.get_skin_details = AsyncMock(return_value={
            "name": "Prime Vandal", "icon": "https://skin", "rarity": "r", "weapon": "Vandal"
        })

        await modal._handle_shop(interaction, auth, "ap")
        interaction.edit_original_response.assert_awaited()

        api_mock.get_shop = AsyncMock(return_value=None)
        await modal._handle_shop(interaction, auth, "ap")
        assert interaction.edit_original_response.await_count >= 2

    async def test_handle_nightmarket_success(self, api_mock):
        modal = ShopModal.__new__(ShopModal)
        modal.api = api_mock
        modal.lang = "en"
        interaction = DummyInteraction(user_id=1)
        auth = SimpleNamespace(game_name="TenZ", tag_line="SEN")

        api_mock.get_nightmarket = AsyncMock(return_value={
            "BonusStoreOffers": [{"OfferID": "offer-2", "DiscountPercent": 20}],
            "BonusStoreRemainingDurationInSeconds": 1800,
        })
        api_mock.get_skin_details = AsyncMock(return_value={
            "name": "Reaver Vandal", "icon": "https://skin", "rarity": "r", "weapon": "Vandal"
        })

        await modal._handle_nightmarket(interaction, auth, "ap")
        interaction.edit_original_response.assert_awaited()


class TestInventoryViewFlows:
    async def test_inventory_modal_submit_success(self, api_mock):
        context = DummyInteraction(user_id=22)
        modal = InventoryModal(api_mock, context, lang="en")
        modal.url_input._value = "https://playvalorant.com/opt_in#access_token=x"
        interaction = DummyInteraction(user_id=22)

        api_mock.auth_with_url = AsyncMock(return_value=(True, "ok", SimpleNamespace(game_name="TenZ", tag_line="SEN", puuid="p", headers={})))
        api_mock.resolve_region = AsyncMock(return_value="ap")
        api_mock.get_inventory = AsyncMock(return_value=["uuid-1"]) 
        modal._resolve_skin_details = AsyncMock(return_value=[{"name": "Skin A", "weapon": "Vandal", "icon": None, "rarity": "r"}])

        await modal.on_submit(interaction)
        interaction.edit_original_response.assert_awaited()

    async def test_inventory_modal_submit_all_failed_and_empty(self, api_mock):
        context = DummyInteraction(user_id=22)
        modal = InventoryModal(api_mock, context, lang="en")
        modal.url_input._value = "https://playvalorant.com/opt_in#access_token=x"
        interaction = DummyInteraction(user_id=22)

        api_mock.auth_with_url = AsyncMock(return_value=(True, "ok", SimpleNamespace(game_name="TenZ", tag_line="SEN", puuid="p", headers={})))
        api_mock.resolve_region = AsyncMock(return_value="ap")
        api_mock.get_inventory = AsyncMock(return_value=None)

        await modal.on_submit(interaction)
        interaction.edit_original_response.assert_awaited()

        api_mock.get_inventory = AsyncMock(return_value=[])
        await modal.on_submit(interaction)
        assert interaction.edit_original_response.await_count >= 2

    async def test_inventory_paginator_navigation(self, api_mock):
        auth = SimpleNamespace(game_name="TenZ", tag_line="SEN")
        interaction = DummyInteraction(user_id=77)
        items = [{"name": f"Skin {i}", "weapon": "Vandal", "icon": None, "rarity": "r"} for i in range(15)]
        view = InventoryPaginatorView(api_mock, auth, "ap", "skins", items, interaction, lang="en")

        assert view.total_pages >= 2
        embeds = view.build_page()
        assert len(embeds) >= 1

        await view._next_page(interaction)
        await view._prev_page(interaction)
        interaction.response.edit_message.assert_awaited()


class TestStatsCogBranches:
    async def test_link_success_and_not_found(self):
        bot = MagicMock()
        bot.v_api = MagicMock()
        cog = StatsCog(bot)
        cog._get_lang = AsyncMock(return_value="en")
        interaction = DummyInteraction(user_id=1)

        bot.v_api.get_account_info = AsyncMock(return_value=None)
        await cog.link.callback(cog, interaction, "TenZ", "SEN")
        interaction.followup.send.assert_awaited_once()

        bot.v_api.get_account_info = AsyncMock(return_value={"status": 200, "data": {"name": "TenZ", "tag": "SEN", "region": "ap"}})
        bot.v_api.link_user = AsyncMock(return_value=True)
        await cog.link.callback(cog, interaction, "TenZ", "SEN")
        assert interaction.followup.send.await_count >= 2

    async def test_stat_slash_branches(self, monkeypatch):
        bot = MagicMock()
        bot.v_api = MagicMock()
        cog = StatsCog(bot)
        cog._get_lang = AsyncMock(return_value="en")
        cog._send_stat_intro = AsyncMock()
        interaction = DummyInteraction(user_id=1)
        bot.v_api.get_user_link = AsyncMock(return_value=None)
        mocked_process = AsyncMock()
        monkeypatch.setattr("cogs.stats.process_and_send_stats", mocked_process)

        # Invalid manual input
        await cog.stat_slash.callback(cog, interaction, None, "A", "a")
        interaction.response.send_message.assert_awaited()

        # Linked user path
        bot.v_api.get_user_link = AsyncMock(return_value=("TenZ", "SEN", "ap"))
        await cog.stat_slash.callback(cog, interaction, None, None, None)
        interaction.response.defer.assert_awaited()
        mocked_process.assert_awaited()

        # Unlinked target user path
        bot.v_api.get_user_link = AsyncMock(return_value=None)
        target_user = SimpleNamespace(id=999, display_name="other")
        await cog.stat_slash.callback(cog, interaction, target_user, None, None)
        assert interaction.response.send_message.await_count >= 2


class TestStatViewComponents:
    async def test_player_stats_pagination_callbacks(self):
        import discord

        p_embed = discord.Embed(title="p")
        m_embed = discord.Embed(title="m")
        view = PlayerStatsPagination(p_embed, m_embed, owner_id=1, lang="en")

        denied = DummyInteraction(user_id=2)
        assert await view.interaction_check(denied) is False

        allowed = DummyInteraction(user_id=1)
        await view._show_history(allowed)
        await view._show_profile(allowed)
        allowed.response.edit_message.assert_awaited()

    async def test_stat_modal_submit_and_error(self, monkeypatch):
        api = MagicMock()
        modal = StatModal(api, lang="en", intro_message=SimpleNamespace(edit=AsyncMock()))
        modal.name_input._value = "TenZ"
        modal.tag_input._value = "SEN"
        interaction = DummyInteraction(user_id=1)

        process_mock = AsyncMock()
        monkeypatch.setattr("views.stat_views.process_and_send_stats", process_mock)
        await modal.on_submit(interaction)
        process_mock.assert_awaited_once()

        interaction2 = DummyInteraction(user_id=1, response_done=True)
        await modal.on_error(interaction2, RuntimeError("boom"))
        interaction2.followup.send.assert_awaited_once()

    async def test_stat_view_check_and_open_modal(self):
        api = MagicMock()
        view = StatView(api, owner_id=1, lang="en")
        denied = DummyInteraction(user_id=2)
        assert await view.interaction_check(denied) is False

        allowed = DummyInteraction(user_id=1)
        await view._open_modal(allowed)
        allowed.response.send_modal.assert_awaited_once()
