"""Tests for utils/__init__.py — ValorantAPI facade."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from utils import ValorantAPI
from utils.riot_auth import AuthResult
from utils.constants import RANK_TIERS, ITEM_TYPE_IDS
from tests.conftest import FakeSession, FakeResponse


@pytest.fixture
def api():
    """ValorantAPI with mocked sub-modules to avoid real I/O."""
    with patch.dict("os.environ", {
        "HENRIK_API_KEY": "test-key",
        "RIOT_REGION": "ap",
        "MONGO_URI": "mongodb://localhost:27017",
    }):
        v = ValorantAPI()
    v.session = FakeSession()
    v.user_manager.collection = AsyncMock()
    return v


class TestGetRankAssets:
    def test_iron_1(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Iron 1")
        assert color == RANK_TIERS["iron"][0]
        assert "/3/" in icon  # base_idx for iron = 3, offset 0

    def test_iron_2(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Iron 2")
        assert "/4/" in icon  # base_idx 3 + offset 1

    def test_iron_3(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Iron 3")
        assert "/5/" in icon  # base_idx 3 + offset 2

    def test_diamond_2(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Diamond 2")
        assert color == RANK_TIERS["diamond"][0]
        assert "/19/" in icon  # base_idx 18 + offset 1

    def test_radiant_no_offset(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Radiant")
        assert color == RANK_TIERS["radiant"][0]
        assert "/27/" in icon  # radiant always offset 0

    def test_unknown_rank_defaults(self):
        api = ValorantAPI()
        color, icon = api.get_rank_assets("Unrated")
        assert color == 0x2b2d31
        assert "/0/" in icon

    def test_case_insensitive(self):
        api = ValorantAPI()
        c1, i1 = api.get_rank_assets("DIAMOND 1")
        c2, i2 = api.get_rank_assets("diamond 1")
        assert c1 == c2
        assert i1 == i2


class TestGetAuthLink:
    def test_returns_string(self):
        api = ValorantAPI()
        link = api.get_auth_link()
        assert isinstance(link, str)
        assert "auth.riotgames.com" in link


class TestDelegation:
    """Verify the facade correctly delegates to sub-modules."""

    async def test_get_stats_delegates(self, api):
        api.henrik.get_stats = AsyncMock(return_value={"status": 200})
        result = await api.get_stats("name", "tag", region="na")
        api.henrik.get_stats.assert_awaited_once_with("name", "tag", api.session, region="na")
        assert result == {"status": 200}

    async def test_get_account_info_delegates(self, api):
        api.henrik.get_account_info = AsyncMock(return_value={"status": 200})
        result = await api.get_account_info("name", "tag")
        api.henrik.get_account_info.assert_awaited_once_with("name", "tag", api.session)

    async def test_link_user_delegates(self, api):
        api.user_manager.link_user = AsyncMock(return_value=True)
        result = await api.link_user(123, "name", "tag", "ap")
        api.user_manager.link_user.assert_awaited_once_with(123, "name", "tag", "ap")
        assert result is True

    async def test_get_language_delegates(self, api):
        api.user_manager.get_language = AsyncMock(return_value="vi")
        result = await api.get_language(123)
        assert result == "vi"


class TestGetInventory:
    async def test_unknown_item_type_returns_empty(self, api):
        result = await api.get_inventory(
            AuthResult("puuid", "name", "tag", {}),
            "nonexistent_type"
        )
        assert result == []

    async def test_shard_mapping_latam_to_na(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.na.a.pvp.net", FakeResponse(
            json_data={"Entitlements": [{"ItemID": "item-1"}]},
            status=200,
        ))
        result = await api.get_inventory(auth, "skins", region="latam")
        assert result == ["item-1"]

    async def test_shard_mapping_br_to_na(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.na.a.pvp.net", FakeResponse(
            json_data={"Entitlements": [{"ItemID": "item-2"}]},
            status=200,
        ))
        result = await api.get_inventory(auth, "skins", region="br")
        assert result == ["item-2"]

    async def test_entitlements_by_types_fallback(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.ap.a.pvp.net", FakeResponse(
            json_data={
                "Entitlements": [],
                "EntitlementsByTypes": [
                    {"Entitlements": [{"ItemID": "fallback-1"}, {"ItemID": "fallback-2"}]}
                ],
            },
            status=200,
        ))
        result = await api.get_inventory(auth, "skins", region="ap")
        assert result == ["fallback-1", "fallback-2"]

    async def test_api_error_returns_none(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.ap.a.pvp.net", FakeResponse(status=403, text="Forbidden"))
        result = await api.get_inventory(auth, "skins", region="ap")
        assert result is None


class TestStorefront:
    async def test_get_shop_extracts_skins_panel(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.ap.a.pvp.net/store/v3/storefront", FakeResponse(
            json_data={
                "SkinsPanelLayout": {"SingleItemOffers": ["offer-1", "offer-2"]},
                "BonusStore": {},
            },
            status=200,
        ))
        result = await api.get_shop(auth, region="ap")
        assert result is not None
        assert "SingleItemOffers" in result

    async def test_get_nightmarket_extracts_bonus_store(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.ap.a.pvp.net/store/v3/storefront", FakeResponse(
            json_data={
                "SkinsPanelLayout": {},
                "BonusStore": {"BonusStoreOffers": [{"OfferID": "nm-1"}]},
            },
            status=200,
        ))
        result = await api.get_nightmarket(auth, region="ap")
        assert result is not None
        assert "BonusStoreOffers" in result

    async def test_storefront_api_failure(self, api):
        auth = AuthResult("puuid", "name", "tag", {"Authorization": "Bearer t"})
        api.session.add("pd.ap.a.pvp.net/store/v3/storefront", FakeResponse(
            status=500, text="Internal Server Error"
        ))
        result = await api.get_shop(auth, region="ap")
        assert result is None
