"""Tests for utils/i18n.py — localization system."""
from utils.i18n import t, STRINGS, DEFAULT_LANG


class TestDefaultLang:
    def test_default_lang_is_vi(self):
        assert DEFAULT_LANG == "vi"


class TestTranslationLookup:
    def test_returns_vietnamese_by_default(self):
        result = t("button_denied")
        assert "không phải của bạn" in result

    def test_returns_vietnamese(self):
        result = t("button_denied", "vi")
        assert "không phải của bạn" in result

    def test_returns_english(self):
        result = t("button_denied", "en")
        assert result == "You cannot use this button."

    def test_unknown_key_returns_key(self):
        result = t("nonexistent_key_xyz", "en")
        assert result == "nonexistent_key_xyz"

    def test_unknown_lang_falls_back_to_default(self):
        result = t("button_denied", "jp")
        assert result == STRINGS["button_denied"]["vi"]


class TestTemplateSubstitution:
    def test_single_variable(self):
        result = t("error_cooldown", "en", retry_after=5)
        assert "5s" in result

    def test_multiple_variables(self):
        result = t("stat_error_account", "en", name="Foo", tag="Bar", error="timeout")
        assert "Foo#Bar" in result
        assert "timeout" in result

    def test_vi_template_substitution(self):
        result = t("link_success", "vi", name="TenZ", tag="SEN")
        assert "TenZ#SEN" in result

    def test_daily_shop_intro_uses_clear_action_labels(self):
        result = t("shop_intro", "vi", mode=t("mode_daily_shop", "vi"))

        assert result.startswith("Đăng nhập Riot để xem cửa hàng hôm nay của bạn.")
        assert "**Cách thực hiện**" in result
        assert "Đăng nhập Riot" in result
        assert "Dán URL" in result
        assert "không lưu mật khẩu" in result
        assert "1️⃣" not in result

    def test_daily_shop_title_is_simple_and_consistent(self):
        assert t("title_daily_shop", "vi") == "Daily Shop"
        assert t("title_daily_shop", "en") == "Daily Shop"


class TestAllStringsHaveBothLanguages:
    def test_every_key_has_en_and_vi(self):
        missing = []
        for key, entry in STRINGS.items():
            if "en" not in entry:
                missing.append(f"{key} missing 'en'")
            if "vi" not in entry:
                missing.append(f"{key} missing 'vi'")
        assert missing == [], f"Missing translations: {missing}"


class TestStringKeysUsedInCode:
    """Spot-check that important keys exist and produce non-empty strings."""

    IMPORTANT_KEYS = [
        "stat_loading", "shop_loading", "loading_hint", "stat_level", "stat_region",
        "stat_peak_rank", "stat_match_history_desc", "stat_win", "stat_loss",
        "btn_profile", "btn_match_history",
        "btn_lookup", "btn_login", "btn_paste", "footer", "shop_session_footer",
        "title_daily_shop", "title_night_market", "title_inventory",
        "stat_modal_title", "stat_modal_name", "stat_modal_tag",
        "shop_modal_title", "nm_modal_title", "inv_modal_title",
        "mode_daily_shop", "mode_night_market",
        "stat_modal_name_ph", "stat_modal_tag_ph",
    ]

    def test_important_keys_exist(self):
        for key in self.IMPORTANT_KEYS:
            assert key in STRINGS, f"Key '{key}' not found in STRINGS"

    def test_important_keys_return_nonempty_strings(self):
        for key in self.IMPORTANT_KEYS:
            for lang in ("en", "vi"):
                result = t(key, lang)
                assert result and result != key, f"t('{key}', '{lang}') returned empty or key"
