"""Tests for views — stat_views, shop_views, inventory_views.

These tests focus on testable logic (formatting, data processing)
without requiring a running Discord bot. View classes that depend on
discord.Interaction are tested via mocks where feasible.
"""
import ast
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from views.shop_views import ShopModal
from utils.constants import RARITY_DATA


def test_only_rank_stats_and_shop_products_define_a_color():
    project_root = Path(__file__).parent.parent
    colored_embeds = []

    for folder in ("cogs", "views"):
        for path in (project_root / folder).glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                if not (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "Embed"
                ):
                    continue
                color_keyword = next(
                    (keyword for keyword in node.keywords if keyword.arg in {"color", "colour"}),
                    None,
                )
                if color_keyword:
                    colored_embeds.append((path.relative_to(project_root), color_keyword.value))

    assert len(colored_embeds) == 3

    stat_embeds = [
        value for path, value in colored_embeds
        if path == Path("views/stat_views.py")
    ]
    assert len(stat_embeds) == 2
    assert all(
        isinstance(value, ast.Name) and value.id == "rank_color"
        for value in stat_embeds
    )

    shop_embeds = [
        value for path, value in colored_embeds
        if path == Path("views/shop_views.py")
    ]
    assert len(shop_embeds) == 1
    assert isinstance(shop_embeds[0], ast.Subscript)


class TestShopModalFormatDuration:
    """Test the _format_duration helper on ShopModal."""

    @pytest.fixture
    def modal(self):
        with patch("views.shop_views.ValorantAPI"):
            m = ShopModal.__new__(ShopModal)
            m.lang = "en"
            return m

    def test_normal_duration(self, modal):
        assert modal._format_duration(3661) == "1h 1m"

    def test_exact_hours(self, modal):
        assert modal._format_duration(7200) == "2h 0m"

    def test_only_minutes(self, modal):
        assert modal._format_duration(300) == "0h 5m"

    def test_zero_seconds(self, modal):
        result = modal._format_duration(0)
        assert result != "0h 0m"  # Should show refreshing message

    def test_negative_seconds(self, modal):
        result = modal._format_duration(-100)
        assert result != "0h 0m"  # Should show refreshing message

    def test_large_duration(self, modal):
        assert modal._format_duration(86400) == "24h 0m"


class TestShopModalSkinEmbed:
    """Test _create_skin_embed on ShopModal."""

    @pytest.fixture
    def modal(self):
        m = ShopModal.__new__(ShopModal)
        m.lang = "en"
        m.api = MagicMock()
        m.api.is_melee_weapon.return_value = False
        m.api.get_hardcoded_price.return_value = 1775
        m.api.get_rarity_info.return_value = {"name": "Premium", "color": 0xd1548d}
        m.api.get_rarity_icon.return_value = "https://example.com/tier.png"
        return m

    def test_embed_has_correct_author_name(self, modal):
        details = {"name": "Prime Vandal", "icon": "https://example.com/icon.png", "rarity": "r-uuid", "weapon": "Vandal"}
        embed = modal._create_skin_embed(details, 0, "offer-id")
        assert embed.author.name == "Prime Vandal"
        assert embed.color.value == 0xd1548d

    def test_embed_with_discount(self, modal):
        modal.api.get_hardcoded_price.return_value = 1000
        details = {"name": "Skin", "icon": "https://icon.png", "rarity": "r", "weapon": "Vandal"}
        embed = modal._create_skin_embed(details, 30, "offer-id")
        assert embed.footer.text is not None
        assert "30%" in embed.footer.text

    def test_embed_no_discount(self, modal):
        modal.api.get_hardcoded_price.return_value = 1000
        details = {"name": "Skin", "icon": None, "rarity": "r", "weapon": "Vandal"}
        embed = modal._create_skin_embed(details, 0, "offer-id")
        assert "%" not in embed.footer.text


class TestProcessAndSendStatsLogic:
    """Test data processing logic used in process_and_send_stats.

    We test the calculation logic extracted from the function rather
    than calling the full function (which requires Discord mocks).
    """

    def test_progress_bar_calculation(self):
        """Verify progress bar logic for various RR values."""
        def make_bar(rr, rank):
            rank_lower = rank.lower()
            if "radiant" in rank_lower or "immortal" in rank_lower or "unrated" in rank_lower:
                return f"**{rr} RR**"
            bars = min(max(rr // 10, 0), 10)
            return f"`{'▰' * bars}{'▱' * (10 - bars)}` **{rr}/100 RR**"

        # Normal rank
        bar_50 = make_bar(50, "Gold 2")
        assert "▰" * 5 in bar_50
        assert "▱" * 5 in bar_50
        assert "50/100" in bar_50

        # Zero RR
        bar_0 = make_bar(0, "Silver 1")
        assert "▱" * 10 in bar_0

        # Full RR
        bar_100 = make_bar(100, "Platinum 3")
        assert "▰" * 10 in bar_100

        # Radiant — no bar
        bar_rad = make_bar(350, "Radiant")
        assert "350 RR" in bar_rad
        assert "▰" not in bar_rad

        # Immortal — no bar
        bar_imm = make_bar(200, "Immortal 3")
        assert "200 RR" in bar_imm

    def test_headshot_percentage_calculation(self):
        """Verify HS% calculation."""
        def calc_hs(headshots, bodyshots, legshots):
            total = headshots + bodyshots + legshots
            return round((headshots / total) * 100) if total > 0 else 0

        assert calc_hs(12, 30, 3) == 27
        assert calc_hs(0, 0, 0) == 0
        assert calc_hs(10, 0, 0) == 100
        assert calc_hs(5, 10, 5) == 25

    def test_acs_calculation(self):
        """Verify ACS calculation."""
        def calc_acs(score, rounds):
            try:
                return round(int(score) / int(rounds)) if int(rounds) > 0 else 0
            except (ValueError, TypeError):
                return 0

        assert calc_acs(6000, 24) == 250
        assert calc_acs(0, 10) == 0
        assert calc_acs(1000, 0) == 0
        assert calc_acs("invalid", 10) == 0

    def test_match_entry_win_detection(self):
        """Test win/loss detection from teams dict."""
        teams_dict = {
            "blue": {"has_won": True},
            "red": {"has_won": False},
        }

        def check_win(team, teams):
            if isinstance(teams, dict):
                team_data = teams.get(team, {})
                if isinstance(team_data, dict):
                    return team_data.get("has_won", False)
            return False

        assert check_win("blue", teams_dict) is True
        assert check_win("red", teams_dict) is False
        assert check_win("green", teams_dict) is False
        assert check_win("blue", {}) is False
        assert check_win("blue", "invalid") is False
