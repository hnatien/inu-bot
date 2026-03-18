"""Tests for utils/valorant_assets.py — asset management."""
import pytest
from unittest.mock import patch

from utils.valorant_assets import ValorantAssets
from utils.constants import RARITY_DATA, MELEE_KEYWORDS
from tests.conftest import FakeSession, FakeResponse


class TestGetRarityInfo:
    def test_known_rarity(self):
        assets = ValorantAssets()
        # Select tier
        info = assets.get_rarity_info("12683d76-48d7-84a3-4e09-6985794f0445")
        assert info["name"] == "Select"
        assert info["gun_price"] == 875

    def test_unknown_rarity(self):
        assets = ValorantAssets()
        info = assets.get_rarity_info("nonexistent-uuid")
        assert info["name"] == "Unknown"
        assert info["color"] == 0x2b2d31

    def test_none_rarity(self):
        assets = ValorantAssets()
        info = assets.get_rarity_info(None)
        assert info["name"] == "Unknown"


class TestGetRarityIcon:
    def test_no_uuid_returns_none(self):
        assets = ValorantAssets()
        assert assets.get_rarity_icon(None) is None

    def test_unknown_uuid_returns_none(self):
        assets = ValorantAssets()
        assert assets.get_rarity_icon("nonexistent") is None

    def test_known_uuid_returns_icon(self):
        assets = ValorantAssets()
        assets.rarity_map["test-uuid"] = {"name": "Premium", "icon": "https://example.com/icon.png"}
        icon = assets.get_rarity_icon("test-uuid")
        assert icon == "https://example.com/icon.png"


class TestGetHardcodedPrice:
    def test_gun_price_for_known_rarity(self):
        assets = ValorantAssets()
        # Premium tier
        price = assets.get_hardcoded_price("60bca009-4182-7998-dee7-b8a2558dc369")
        assert price == 1775

    def test_melee_price_for_known_rarity(self):
        assets = ValorantAssets()
        # Premium tier
        price = assets.get_hardcoded_price("60bca009-4182-7998-dee7-b8a2558dc369", is_melee=True)
        assert price == 3550

    def test_override_takes_priority(self):
        assets = ValorantAssets()
        assets.price_overrides["special-skin-uuid"] = 9999
        price = assets.get_hardcoded_price(
            "60bca009-4182-7998-dee7-b8a2558dc369",
            level_uuid="special-skin-uuid"
        )
        assert price == 9999

    def test_unknown_rarity_returns_zero(self):
        assets = ValorantAssets()
        price = assets.get_hardcoded_price("unknown-rarity")
        assert price == 0


class TestIsMeleeWeapon:
    def test_melee_weapon_type(self):
        assert ValorantAssets.is_melee_weapon("Melee", "Standard Melee") is True

    def test_melee_keyword_in_name(self):
        assert ValorantAssets.is_melee_weapon("", "Prime Karambit") is True
        assert ValorantAssets.is_melee_weapon("", "RGX Butterfly Knife") is True
        assert ValorantAssets.is_melee_weapon("", "Reaver Dagger") is True

    def test_non_melee(self):
        assert ValorantAssets.is_melee_weapon("Rifle", "Vandal") is False
        assert ValorantAssets.is_melee_weapon("Pistol", "Classic") is False

    def test_case_insensitive(self):
        assert ValorantAssets.is_melee_weapon("MELEE", "KNIFE") is True


class TestGetSkinDetails:
    async def test_cache_hit(self):
        assets = ValorantAssets()
        assets.skin_map["cached-uuid"] = {
            "name": "Prime Vandal",
            "icon": "https://example.com/icon.png",
            "rarity": "some-uuid",
            "weapon": "Vandal",
        }
        session = FakeSession()
        result = await assets.get_skin_details("cached-uuid", session)
        assert result is not None
        assert result["name"] == "Prime Vandal"

    async def test_cache_miss_fetches_from_api(self):
        assets = ValorantAssets()
        session = FakeSession()
        session.add("skinlevels/new-uuid", FakeResponse(
            json_data={
                "status": 200,
                "data": {
                    "displayName": "Reaver Vandal",
                    "displayIcon": "https://example.com/reaver.png",
                    "contentTierUuid": "tier-uuid",
                    "weapon": "Vandal",
                },
            },
            status=200,
        ))
        result = await assets.get_skin_details("new-uuid", session)
        assert result is not None
        assert result["name"] == "Reaver Vandal"

    async def test_empty_uuid_returns_none(self):
        assets = ValorantAssets()
        session = FakeSession()
        result = await assets.get_skin_details("", session)
        assert result is None

    async def test_api_error_returns_none(self):
        assets = ValorantAssets()
        session = FakeSession()
        session.add("skinlevels/fail-uuid", FakeResponse(status=500, json_data={}))
        result = await assets.get_skin_details("fail-uuid", session)
        assert result is None


class TestFetchAllData:
    async def test_populates_skin_map(self):
        assets = ValorantAssets()
        session = FakeSession()
        session.add("valorant-api.com/v1/weapons", FakeResponse(
            json_data={
                "status": 200,
                "data": [
                    {
                        "displayName": "Vandal",
                        "skins": [
                            {
                                "uuid": "skin-1",
                                "displayName": "Prime Vandal",
                                "displayIcon": "https://example.com/prime.png",
                                "contentTierUuid": "tier-1",
                                "levels": [{"uuid": "level-1"}],
                                "chromas": [
                                    {
                                        "uuid": "chroma-1",
                                        "displayName": "Prime Vandal (Red)",
                                        "displayIcon": "https://example.com/prime_red.png",
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
            status=200,
        ))
        session.add("valorant-api.com/v1/contenttiers", FakeResponse(
            json_data={
                "status": 200,
                "data": [
                    {"uuid": "tier-1", "devName": "Premium", "displayIcon": "https://example.com/tier.png"}
                ],
            },
            status=200,
        ))
        await assets.fetch_all_data(session)

        assert "skin-1" in assets.skin_map
        assert "level-1" in assets.skin_map
        assert "chroma-1" in assets.skin_map
        assert assets.skin_map["skin-1"]["name"] == "Prime Vandal"
        assert assets.skin_map["skin-1"]["weapon"] == "Vandal"
        assert "tier-1" in assets.rarity_map
        assert assets.rarity_map["tier-1"]["name"] == "Premium"
