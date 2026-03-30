"""Additional audit tests for cogs/views/facade coverage and behavior."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cogs import CogBase
from cogs.info import HelpView, InfoCog, _build_help_embed, _build_update_embed, setup as setup_info
from cogs.inventory import InventoryCog, setup as setup_inventory
from cogs.shop import ShopCog, setup as setup_shop
from cogs.stats import StatsCog, setup as setup_stats
from utils import ValorantAPI
from utils.riot_auth import AuthResult
from views.base_views import BaseView


class DummyInteraction:
    def __init__(self, user_id: int = 1, response_done: bool = False):
        self.user = SimpleNamespace(
            id=user_id,
            display_avatar=SimpleNamespace(url="https://avatar.example/u.png"),
            display_name=f"u{user_id}",
        )
        self.author = self.user
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
def fake_bot():
    bot = MagicMock()
    bot.v_api = MagicMock()
    bot.add_cog = AsyncMock()
    return bot


class TestBaseView:
    async def test_on_timeout_disables_and_notifies(self):
        view = BaseView(timeout=1, lang="en")
        btn = __import__("discord").ui.Button(label="X")
        view.add_item(btn)
        msg = SimpleNamespace(edit=AsyncMock(), reply=AsyncMock())
        view.message = msg

        await view.on_timeout()

        assert btn.disabled is True
        msg.edit.assert_awaited_once()
        msg.reply.assert_awaited_once()


class TestFacadeCoverage:
    async def test_ssl_ctx_cached(self):
        with patch.dict("os.environ", {"HENRIK_API_KEY": "k", "MONGO_URI": "m", "RIOT_REGION": "ap"}):
            api = ValorantAPI()
        c1 = api._get_ssl_ctx()
        c2 = api._get_ssl_ctx()
        assert c1 is c2

    async def test_init_session_reuses_existing(self):
        with patch.dict("os.environ", {"HENRIK_API_KEY": "k", "MONGO_URI": "m", "RIOT_REGION": "ap"}):
            api = ValorantAPI()
        existing = MagicMock(closed=False)
        api.session = existing
        session = await api.init_session()
        assert session is existing

    async def test_resolve_region_fallback(self):
        with patch.dict("os.environ", {"HENRIK_API_KEY": "k", "MONGO_URI": "m", "RIOT_REGION": "ap"}):
            api = ValorantAPI()
        api.get_account_info = AsyncMock(return_value={"status": 500})
        auth = AuthResult("p", "n", "t", {})
        assert await api.resolve_region(auth) == api.region

    async def test_delegate_helpers(self):
        with patch.dict("os.environ", {"HENRIK_API_KEY": "k", "MONGO_URI": "m", "RIOT_REGION": "ap"}):
            api = ValorantAPI()
        api.session = MagicMock()
        api.auth.auth_with_url = AsyncMock(return_value=(True, "ok", None))
        api.henrik.get_recent_matches = AsyncMock(return_value={"status": 200})
        api.assets.get_skin_details = AsyncMock(return_value={"name": "skin"})
        api.user_manager.get_user_link = AsyncMock(return_value=("n", "t", "ap"))
        api.user_manager.unlink_user = AsyncMock(return_value=True)
        api.user_manager.set_language = AsyncMock(return_value=True)

        await api.auth_with_url("https://playvalorant.com", lang="en")
        await api.get_recent_matches("n", "t", region="ap")
        await api.get_skin_details("uuid")
        assert await api.get_user_link(1) == ("n", "t", "ap")
        assert await api.unlink_user(1) is True
        assert await api.set_language(1, "vi") is True


class TestCogBase:
    async def test_get_lang_from_api(self):
        cog = CogBase()
        cog.api = MagicMock()
        cog.api.get_language = AsyncMock(return_value="vi")
        assert await cog._get_lang(10) == "vi"


class TestInfoCog:
    async def test_build_help_update_embed(self):
        e1 = _build_help_embed("en")
        e2 = _build_update_embed("en")
        assert e1.title
        assert e2.title
        assert "v" in (e2.description or "")

    async def test_help_view_owner_check_denied(self):
        view = HelpView(lang="en", owner_id=1)
        interaction = DummyInteraction(user_id=2)
        ok = await view.interaction_check(interaction)
        assert ok is False
        interaction.response.send_message.assert_awaited_once()

    async def test_help_view_buttons_edit_message(self):
        view = HelpView(lang="en", owner_id=1)
        interaction = DummyInteraction(user_id=1)
        await view.stats_button.callback(interaction)
        await view.shop_button.callback(interaction)
        await view.inventory_button.callback(interaction)
        await view.misc_button.callback(interaction)
        assert interaction.response.edit_message.await_count == 4

    async def test_info_send_help_and_update_for_interaction(self, fake_bot, monkeypatch):
        cog = InfoCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        interaction = DummyInteraction(user_id=10)
        monkeypatch.setattr("cogs.info.discord.Interaction", DummyInteraction)

        await cog._send_help(interaction)
        await cog._send_update(interaction)
        interaction.response.send_message.assert_awaited()

    async def test_info_language_prefix(self, fake_bot):
        cog = InfoCog(fake_bot)
        fake_bot.v_api.set_language = AsyncMock(return_value=True)
        ctx = DummyContext(user_id=10)
        await cog.language_prefix.callback(cog, ctx, "xx")
        await cog.language_prefix.callback(cog, ctx, "vi")
        assert ctx.send.await_count == 2

    async def test_info_setup(self, fake_bot):
        await setup_info(fake_bot)
        fake_bot.add_cog.assert_awaited_once()

    async def test_info_command_wrappers(self, fake_bot):
        cog = InfoCog(fake_bot)
        cog._send_help = AsyncMock()
        cog._send_update = AsyncMock()
        interaction = DummyInteraction(user_id=3)
        ctx = DummyContext(user_id=3)

        await cog.help_slash.callback(cog, interaction)
        await cog.help_prefix.callback(cog, ctx)
        await cog.update_slash.callback(cog, interaction)
        await cog.update_prefix.callback(cog, ctx)

        assert cog._send_help.await_count == 2
        assert cog._send_update.await_count == 2

    async def test_language_slash(self, fake_bot):
        cog = InfoCog(fake_bot)
        fake_bot.v_api.set_language = AsyncMock(return_value=True)
        interaction = DummyInteraction(user_id=7)
        lang_choice = SimpleNamespace(value="en")
        await cog.language_slash.callback(cog, interaction, lang_choice)
        interaction.response.send_message.assert_awaited_once()


class TestInventoryCog:
    async def test_send_intro_interaction_and_prefix(self, fake_bot, monkeypatch):
        cog = InventoryCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        fake_bot.v_api.get_auth_link.return_value = "https://auth"
        monkeypatch.setattr("cogs.inventory.discord.Interaction", DummyInteraction)

        interaction = DummyInteraction(user_id=20)
        await cog._send_intro(interaction)
        interaction.response.send_message.assert_awaited_once()

        ctx = DummyContext(user_id=20)
        await cog._send_intro(ctx)
        ctx.send.assert_awaited_once()

    async def test_inventory_setup(self, fake_bot):
        await setup_inventory(fake_bot)
        fake_bot.add_cog.assert_awaited_once()

    async def test_inventory_command_wrappers(self, fake_bot):
        cog = InventoryCog(fake_bot)
        cog._send_intro = AsyncMock()
        interaction = DummyInteraction(user_id=1)
        ctx = DummyContext(user_id=1)

        await cog.inventory_slash.callback(cog, interaction)
        await cog.inventory_prefix.callback(cog, ctx)
        assert cog._send_intro.await_count == 2


class TestShopCog:
    async def test_send_safety_message_both_context_types(self, fake_bot, monkeypatch):
        cog = ShopCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        monkeypatch.setattr("cogs.shop.discord.Interaction", DummyInteraction)

        interaction = DummyInteraction(user_id=30)
        await cog._send_safety_msg(interaction)
        interaction.response.send_message.assert_awaited_once()

        ctx = DummyContext(user_id=30)
        await cog._send_safety_msg(ctx)
        ctx.send.assert_awaited_once()

    async def test_send_intro_both_modes(self, fake_bot, monkeypatch):
        cog = ShopCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        fake_bot.v_api.get_auth_link.return_value = "https://auth"
        monkeypatch.setattr("cogs.shop.discord.Interaction", DummyInteraction)

        interaction = DummyInteraction(user_id=30)
        await cog._send_intro(interaction, mode="shop")
        await cog._send_intro(interaction, mode="nightmarket")
        assert interaction.response.send_message.await_count == 2

    async def test_shop_setup(self, fake_bot):
        await setup_shop(fake_bot)
        fake_bot.add_cog.assert_awaited_once()

    async def test_shop_command_wrappers(self, fake_bot):
        cog = ShopCog(fake_bot)
        cog._send_intro = AsyncMock()
        cog._send_safety_msg = AsyncMock()
        interaction = DummyInteraction(user_id=1)
        ctx = DummyContext(user_id=1)

        await cog.shop_slash.callback(cog, interaction)
        await cog.nightmarket_slash.callback(cog, interaction)
        await cog.safety_slash.callback(cog, interaction)
        await cog.safety_prefix.callback(cog, ctx)
        await cog.shop_prefix.callback(cog, ctx)
        await cog.nightmarket_prefix.callback(cog, ctx)

        assert cog._send_intro.await_count == 4
        assert cog._send_safety_msg.await_count == 2


class TestStatsCog:
    async def test_link_validation_and_unlink(self, fake_bot):
        cog = StatsCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        interaction = DummyInteraction(user_id=40)

        await cog.link.callback(cog, interaction, "", "12")
        interaction.response.send_message.assert_awaited_once()

        fake_bot.v_api.unlink_user = AsyncMock(return_value=True)
        await cog.unlink.callback(cog, interaction)
        assert interaction.response.send_message.await_count >= 2

    async def test_send_stat_intro_interaction_and_prefix(self, fake_bot, monkeypatch):
        cog = StatsCog(fake_bot)
        monkeypatch.setattr("cogs.stats.discord.Interaction", DummyInteraction)

        interaction = DummyInteraction(user_id=40)
        await cog._send_stat_intro(interaction, lang="en")
        interaction.response.send_message.assert_awaited_once()

        ctx = DummyContext(user_id=40)
        await cog._send_stat_intro(ctx, lang="en")
        ctx.send.assert_awaited_once()

    async def test_stat_prefix_paths(self, fake_bot):
        cog = StatsCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        ctx = DummyContext(user_id=50)

        fake_bot.v_api.get_user_link = AsyncMock(return_value=None)
        cog._send_stat_intro = AsyncMock()
        await cog.stat_prefix.callback(cog, ctx)
        cog._send_stat_intro.assert_awaited_once()

    async def test_stats_setup(self, fake_bot):
        await setup_stats(fake_bot)
        fake_bot.add_cog.assert_awaited_once()

    async def test_unlink_failure_branch(self, fake_bot):
        cog = StatsCog(fake_bot)
        cog._get_lang = AsyncMock(return_value="en")
        interaction = DummyInteraction(user_id=55)
        fake_bot.v_api.unlink_user = AsyncMock(return_value=False)

        await cog.unlink.callback(cog, interaction)
        interaction.response.send_message.assert_awaited_once()
