"""Tests for utils/constants.py — static data integrity."""
from utils.constants import (
    RARITY_DATA, MELEE_KEYWORDS, RANK_TIERS,
    ITEM_TYPE_IDS, VP_ICON_URL, INVENTORY_ITEMS_PER_PAGE,
    RANK_ICON_BASE, DEFAULT_RANK_ICON,
)


class TestRarityData:
    EXPECTED_TIERS = ["Select", "Deluxe", "Premium", "Exclusive", "Ultra"]

    def test_has_five_tiers(self):
        assert len(RARITY_DATA) == 5

    def test_tier_names(self):
        names = [v["name"] for v in RARITY_DATA.values()]
        assert sorted(names) == sorted(self.EXPECTED_TIERS)

    def test_each_tier_has_required_fields(self):
        for uuid, tier in RARITY_DATA.items():
            assert "name" in tier
            assert "color" in tier
            assert "gun_price" in tier
            assert "melee_price" in tier

    def test_melee_price_is_double_gun_price(self):
        for uuid, tier in RARITY_DATA.items():
            assert tier["melee_price"] == tier["gun_price"] * 2, (
                f"{tier['name']}: melee ({tier['melee_price']}) != 2x gun ({tier['gun_price']})"
            )

    def test_prices_are_positive(self):
        for uuid, tier in RARITY_DATA.items():
            assert tier["gun_price"] > 0
            assert tier["melee_price"] > 0

    def test_colors_are_valid_hex(self):
        for uuid, tier in RARITY_DATA.items():
            assert 0 <= tier["color"] <= 0xFFFFFF


class TestMeleeKeywords:
    def test_contains_common_melee_types(self):
        assert "knife" in MELEE_KEYWORDS
        assert "karambit" in MELEE_KEYWORDS
        assert "axe" in MELEE_KEYWORDS

    def test_all_lowercase(self):
        for kw in MELEE_KEYWORDS:
            assert kw == kw.lower()


class TestRankTiers:
    EXPECTED_RANKS = [
        "iron", "bronze", "silver", "gold", "platinum",
        "diamond", "ascendant", "immortal", "radiant",
    ]

    def test_all_ranks_present(self):
        for rank in self.EXPECTED_RANKS:
            assert rank in RANK_TIERS

    def test_tier_structure(self):
        for rank, (color, base_idx) in RANK_TIERS.items():
            assert isinstance(color, int)
            assert isinstance(base_idx, int)
            assert 0 <= color <= 0xFFFFFF
            assert base_idx >= 0

    def test_radiant_is_highest_index(self):
        _, radiant_idx = RANK_TIERS["radiant"]
        for rank, (_, idx) in RANK_TIERS.items():
            if rank != "radiant":
                assert idx < radiant_idx


class TestItemTypeIDs:
    EXPECTED_CATEGORIES = ["skins", "agents", "buddies", "cards", "sprays", "titles"]

    def test_all_categories_present(self):
        for cat in self.EXPECTED_CATEGORIES:
            assert cat in ITEM_TYPE_IDS

    def test_uuids_are_valid_format(self):
        import re
        uuid_re = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        for cat, uid in ITEM_TYPE_IDS.items():
            assert uuid_re.match(uid), f"{cat} has invalid UUID: {uid}"


class TestMiscConstants:
    def test_vp_icon_url_is_valid(self):
        assert VP_ICON_URL.startswith("https://")
        assert "valorant-api.com" in VP_ICON_URL

    def test_inventory_items_per_page_positive(self):
        assert INVENTORY_ITEMS_PER_PAGE > 0

    def test_rank_icon_base_url(self):
        assert RANK_ICON_BASE.startswith("https://")

    def test_default_rank_icon_url(self):
        assert DEFAULT_RANK_ICON.startswith(RANK_ICON_BASE)
        assert DEFAULT_RANK_ICON.endswith(".png")
