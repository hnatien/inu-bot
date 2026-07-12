from typing import Any, Dict, Union

DEFAULT_LANG = "vi"

STRINGS: Dict[str, Dict[str, str]] = {
    "error_cooldown": {
        "vi": "Lệnh đang hồi chiêu, thử lại sau {retry_after}s nhé.",
        "en": "This command is on cooldown. Try again in {retry_after}s.",
    },
    "error_generic": {
        "vi": "Có lỗi xảy ra rồi, thử lại sau nhé.",
        "en": "An error occurred while executing this command.",
    },
    "button_denied": {
        "vi": "Nút này không phải của bạn đâu nhé.",
        "en": "You cannot use this button.",
    },

    "auth_invalid_url": {
        "vi": "URL không hợp lệ. Vui lòng copy URL từ trang `playvalorant.com`.",
        "en": "Invalid URL. Please copy the URL from the `playvalorant.com` page.",
    },
    "auth_no_token": {
        "vi": "Không tìm thấy Access Token. Bạn copy lại toàn bộ URL nhé.",
        "en": "Access Token not found. Please copy the entire URL.",
    },
    "auth_entitlements_error": {
        "vi": "Lỗi xác thực ({status}): {message}",
        "en": "Entitlements Error ({status}): {message}",
    },
    "auth_success": {
        "vi": "Xác thực thành công!",
        "en": "Authentication successful!",
    },
    "auth_no_user": {
        "vi": "Không tìm thấy User ID.",
        "en": "User ID not found.",
    },
    "auth_system_error": {
        "vi": "Lỗi hệ thống, thử lại sau nhé.",
        "en": "System error during authentication. Please try again.",
    },

    "shop_modal_title": {
        "vi": "Mở Daily Shop",
        "en": "Open Daily Shop",
    },
    "nm_modal_title": {
        "vi": "Xác thực Night Market",
        "en": "NIGHT MARKET Authentication",
    },
    "shop_modal_label": {
        "vi": "URL sau khi đăng nhập",
        "en": "URL after signing in",
    },
    "shop_error_no_data": {
        "vi": "Không lấy được dữ liệu Daily Shop từ Riot.",
        "en": "Could not retrieve Daily Shop data from Riot.",
    },
    "shop_header": {
        "vi": "**Tài khoản:** {account}\n**Làm mới sau:** {time}",
        "en": "**Account:** {account}\n**Refreshes in:** {time}",
    },
    "shop_no_skins": {
        "vi": "Không tìm thấy skin nào trong Shop.",
        "en": "No skins found in your Shop.",
    },
    "nm_error_no_data": {
        "vi": "Hiện không có Night Market hoặc không lấy được dữ liệu.",
        "en": "Night Market is currently unavailable or data could not be retrieved.",
    },
    "nm_header": {
        "vi": "**Tài khoản:** {account}\n**Kết thúc sau:** {time}",
        "en": "**Account:** {account}\n**Ends in:** {time}",
    },
    "nm_no_skins": {
        "vi": "Không tìm thấy skin nào trong Night Market.",
        "en": "No skins found in Night Market.",
    },
    "discount": {
        "vi": "**Giảm {percent}%**",
        "en": "**Discount: {percent}%**",
    },
    "btn_login": {
        "vi": "Đăng nhập Riot",
        "en": "Sign in to Riot",
    },
    "btn_paste": {
        "vi": "Dán URL",
        "en": "Paste URL",
    },
    "footer": {
        "vi": "Inu Bot",
        "en": "Powered by Inu Bot",
    },
    "shop_intro": {
        "vi": (
            "Đăng nhập Riot để xem {mode}.\n\n"
            "**Cách thực hiện**\n"
            "`1` Chọn **Đăng nhập Riot**\n"
            "`2` Sao chép toàn bộ URL sau khi đăng nhập\n"
            "`3` Quay lại và chọn **Dán URL**\n\n"
            "🔒 Bot không lưu mật khẩu hoặc thông tin đăng nhập. "
            "Dùng `/safety` để tìm hiểu thêm."
        ),
        "en": (
            "Sign in to Riot to view your current **{mode}**.\n\n"
            "**How it works**\n"
            "`1` Select **Sign in to Riot**\n"
            "`2` Copy the entire URL after signing in\n"
            "`3` Return here and select **Paste URL**\n\n"
            "🔒 The bot never stores your password or sign-in details. "
            "Use `/safety` to learn more."
        ),
    },
    "shop_session_footer": {
        "vi": "Inu Bot • Phiên có hiệu lực trong 5 phút",
        "en": "Inu Bot • Session expires in 5 minutes",
    },
    "safety_title": {
        "vi": "VỀ BẢO MẬT",
        "en": "SECURITY EXPLANATION",
    },
    "safety_desc": {
        "vi": (
            "Bot sử dụng **OAuth2 Implicit Grant** của Riot Games — "
            "giống hệt cách tracker.gg và các ứng dụng uy tín khác đang dùng.\n\n"
            "**Tại sao an toàn?**\n"
            "1. **Không cần mật khẩu:** Bạn đăng nhập trên `auth.riotgames.com`, bot không can thiệp gì.\n"
            "2. **Token tạm thời:** Link bạn gửi chỉ chứa *Access Token* — mã tạm thời chỉ đọc được dữ liệu cửa hàng.\n"
            "3. **Không lưu trữ:** Token chỉ giữ trong RAM và bị xóa ngay khi xong.\n"
            "4. **Zero Logs:** Không Token nào được ghi vào database hay file log.\n\n"
            "*Nên bật xác thực 2 lớp (2FA) cho tài khoản Riot nhé.*"
        ),
        "en": (
            "This system uses Riot Games' **OAuth2 Implicit Grant** mechanism, similar to how websites like "
            "tracker.gg and other reputable open-source applications operate.\n\n"
            "**Why is this method safe?**\n"
            "1. **No Password Required:** You sign in directly on `auth.riotgames.com`. The bot does not interfere.\n"
            "2. **Token-Based:** The link only contains an *Access Token* — a temporary read-only identifier.\n"
            "3. **No Storage:** The bot uses the Token in memory (RAM) and discards it immediately after the session.\n"
            "4. **Zero Logs:** No Token is ever written to the database.\n\n"
            "*Always enable Two-Factor Authentication (2FA) on your Riot account for maximum security.*"
        ),
    },

    "link_invalid_id": {
        "vi": "Riot ID không hợp lệ. Tên 1-16 ký tự, tag 3-5 ký tự.",
        "en": "Invalid Riot ID format. Name must be 1-16 chars, tag 3-5 chars.",
    },
    "link_not_found": {
        "vi": "Không tìm thấy tài khoản **{name}#{tag}**. Kiểm tra lại nhé.",
        "en": "Could not find account **{name}#{tag}**. Please check again.",
    },
    "link_success": {
        "vi": "Đã liên kết với **{name}#{tag}** thành công!",
        "en": "Successfully linked your account to **{name}#{tag}**!",
    },
    "link_db_error": {
        "vi": "Không lưu được liên kết. Thử lại sau nhé.",
        "en": "Failed to save account link. Please try again later.",
    },
    "unlink_success": {
        "vi": "Đã hủy liên kết tài khoản.",
        "en": "Successfully unlinked your account.",
    },
    "unlink_error": {
        "vi": "Bạn chưa liên kết tài khoản nào.",
        "en": "You don't have a linked account.",
    },
    "user_not_linked": {
        "vi": "{name} chưa liên kết tài khoản Valorant.",
        "en": "{name} has not linked their Valorant account yet.",
    },

    "stat_intro": {
        "vi": (
            "> Truy vấn trực tiếp từ server Riot Games.\n"
            "Nhấn nút bên dưới để bắt đầu nhé.\n\n"
            "⏱️ Nút tra cứu sẽ hết hạn sau 5 phút.\n\n"
            "**DỮ LIỆU BAO GỒM:**\n"
            "```yaml\n"
            "- Level, Rank & Rank Rating (RR)\n"
            "- K/D/A, Combat Score (ACS)\n"
            "- Lịch sử 5 trận gần nhất\n"
            "```\n"
            "TIP: Dùng `/link` để liên kết tài khoản và bỏ qua bước này!"
        ),
        "en": (
            "> Directly retrieves data from Riot Games server.\n"
            "Please click the button below to start.\n\n"
            "⏱️ The lookup button expires after 5 minutes.\n\n"
            "**AVAILABLE DATA INCLUDES:**\n"
            "```yaml\n"
            "- Profile Level, Rank & Rank Rating (RR)\n"
            "- Kills/Deaths/Assists (K/D/A), Combat Score (ACS)\n"
            "- Results & Match History for the last 5 games\n"
            "```\n"
            "TIP: Use `/link` to connect your account and skip this step next time!"
        ),
    },
    "stat_error_account": {
        "vi": "Không tìm thấy tài khoản **{name}#{tag}**.\nChi tiết: {error}",
        "en": "Could not find account **{name}#{tag}**.\nDetails: {error}",
    },
    "stat_error_rank": {
        "vi": (
            "Không có dữ liệu rank cho **{name}#{tag}**.\nChi tiết: {error}\n"
            "*Người chơi cần đấu ít nhất 1 trận rank gần đây.*"
        ),
        "en": (
            "Could not find rank data for **{name}#{tag}**.\nDetails: {error}\n"
            "*Ensure the player has played at least 1 recent competitive match.*"
        ),
    },
    "stat_no_matches": {
        "vi": "Không có trận đấu gần đây.",
        "en": "No recent matches found.",
    },
    "stat_match_history_desc": {
        "vi": "{name}#{tag} · 5 trận gần nhất",
        "en": "{name}#{tag} · 5 most recent matches",
    },
    "stat_win": {
        "vi": "Thắng",
        "en": "Win",
    },
    "stat_loss": {
        "vi": "Thua",
        "en": "Loss",
    },
    "stat_level": {
        "vi": "Cấp độ",
        "en": "Level",
    },
    "stat_region": {
        "vi": "Khu vực",
        "en": "Region",
    },
    "stat_peak_rank": {
        "vi": "Rank cao nhất",
        "en": "Peak rank",
    },
    "stat_modal_title": {
        "vi": "TRA CỨU VALORANT",
        "en": "VALORANT STATS LOOKUP",
    },
    "stat_modal_name": {
        "vi": "Tên trong game (Riot ID)",
        "en": "In-game Name (Riot ID)",
    },
    "stat_modal_tag": {
        "vi": "Tagline (không có #)",
        "en": "Tagline (without #)",
    },
    "stat_modal_error": {
        "vi": "Có lỗi xảy ra: `{error}`",
        "en": "An error occurred: `{error}`",
    },

    "help_title": {"vi": "Trợ giúp", "en": "Help"},
    "help_desc": {
        "vi": "Chọn một danh mục bên dưới để xem hướng dẫn và lệnh có sẵn.",
        "en": "Choose a category below to view its guide and available commands.",
    },
    "help_category_label": {"vi": "Danh mục", "en": "Categories"},
    "help_stat_label": {"vi": "Thống kê", "en": "Stats"},
    "help_stat_sub": {
        "vi": "`/stat` · Rank, RR và lịch sử trận đấu",
        "en": "`/stat` · Rank, RR, and match history",
    },
    "help_shop_label": {"vi": "Cửa hàng", "en": "Shop"},
    "help_shop_sub": {
        "vi": "`/shop` · Daily Shop và Night Market",
        "en": "`/shop` · Daily Shop and Night Market",
    },
    "help_inv_label": {"vi": "Kho đồ", "en": "Inventory"},
    "help_inv_sub": {
        "vi": "`/inventory` · Xem và lọc skin đang sở hữu",
        "en": "`/inventory` · Browse and filter owned skins",
    },
    "help_misc_label": {"vi": "Tiện ích", "en": "Utilities"},
    "help_misc_sub": {
        "vi": "`/help` · Ngôn ngữ, cập nhật và các lệnh khác",
        "en": "`/help` · Language, updates, and other commands",
    },
    "help_stat_title": {"vi": "Thống kê", "en": "Stats"},
    "help_stat_desc": {
        "vi": (
            "`/stat` — Xem thống kê của tài khoản đã liên kết\n"
            "`/stat user:@user` — Xem thống kê người khác\n"
            "`/stat name:Tên tag:Tag` — Tra cứu bằng Riot ID\n\n"
            "**Liên kết tài khoản**\n"
            "`/link name:Tên tag:Tag` — Liên kết Riot ID\n"
            "`/unlink` — Hủy liên kết"
        ),
        "en": (
            "`/stat` — View stats for your linked account\n"
            "`/stat user:@user` — View another user's stats\n"
            "`/stat name:Name tag:Tag` — Look up a Riot ID\n\n"
            "**Account linking**\n"
            "`/link name:Name tag:Tag` — Link a Riot ID\n"
            "`/unlink` — Unlink your account"
        ),
    },
    "help_shop_title": {"vi": "Cửa hàng", "en": "Shop"},
    "help_shop_desc": {
        "vi": (
            "`/shop` — Xem Daily Shop\n"
            "`/nightmarket` — Xem Night Market\n"
            "`/safety` — Tìm hiểu về bảo mật\n\n"
            "**Cách sử dụng**\n"
            "`1` Đăng nhập Riot bằng nút được cung cấp\n"
            "`2` Sao chép toàn bộ URL sau khi đăng nhập\n"
            "`3` Quay lại Discord và dán URL\n\n"
            "Bot không lưu mật khẩu hoặc thông tin đăng nhập."
        ),
        "en": (
            "`/shop` — View Daily Shop\n"
            "`/nightmarket` — View Night Market\n"
            "`/safety` — Learn about security\n\n"
            "**How to use**\n"
            "`1` Sign in to Riot using the provided button\n"
            "`2` Copy the entire URL after signing in\n"
            "`3` Return to Discord and paste the URL\n\n"
            "The bot never stores your password or sign-in details."
        ),
    },
    "help_inv_title": {"vi": "Kho đồ", "en": "Inventory"},
    "help_inv_desc": {
        "vi": (
            "`/inventory` — Xem các skin đang sở hữu\n\n"
            "Bạn có thể lọc theo loại vũ khí và duyệt từng trang. "
            "Quá trình đăng nhập giống Daily Shop; bot không lưu thông tin đăng nhập."
        ),
        "en": (
            "`/inventory` — View your owned skins\n\n"
            "Filter by weapon type and browse results by page. "
            "Sign-in works like Daily Shop; the bot never stores your sign-in details."
        ),
    },
    "help_misc_title": {"vi": "Tiện ích", "en": "Utilities"},
    "help_misc_desc": {
        "vi": (
            "`/help` — Mở menu trợ giúp\n"
            "`/update` — Xem các thay đổi mới nhất\n"
            "`/language` — Đổi ngôn ngữ\n\n"
            "Bạn cũng có thể dùng prefix `!`, ví dụ `!stat` hoặc `!shop`."
        ),
        "en": (
            "`/help` — Open the help menu\n"
            "`/update` — View the latest changes\n"
            "`/language` — Change language\n\n"
            "You can also use the `!` prefix, for example `!stat` or `!shop`."
        ),
    },
    "update_title": {
        "vi": "CẬP NHẬT MỚI NHẤT",
        "en": "LATEST UPDATES",
    },
    "lang_set": {
        "vi": "Đã chuyển sang **Tiếng Việt** 🇻🇳",
        "en": "Switched to **English** 🇬🇧",
    },

    "inv_intro": {
        "vi": (
            "Để xem **Inventory**, hãy làm 3 bước:\n\n"
            "1️⃣ Nhấn **Đăng nhập Riot** → đăng nhập tài khoản\n"
            "2️⃣ Sau khi chuyển hướng, **copy toàn bộ URL** trên thanh địa chỉ\n"
            "3️⃣ Nhấn **Dán Link** → paste URL vừa copy\n\n"
            "⏱️ Nút sẽ hết hạn sau 5 phút, chạy lại lệnh nếu quá hạn.\n\n"
            "*Dùng `/safety` để tìm hiểu về bảo mật.*"
        ),
        "en": (
            "To view your **Inventory**, follow 3 steps:\n\n"
            "1️⃣ Click **Sign in to Riot** → sign in to your account\n"
            "2️⃣ After redirect, **copy the entire URL** from the address bar\n"
            "3️⃣ Click **Paste Link** → paste the URL you copied\n\n"
            "⏱️ Buttons expire after 5 minutes, run the command again when needed.\n\n"
            "*Use `/safety` to learn more about security.*"
        ),
    },
    "inv_modal_title": {
        "vi": "Xác thực Inventory",
        "en": "INVENTORY Authentication",
    },
    "inv_header": {
        "vi": "> **Tài khoản:** `{account}`\n> **Danh mục:** `{category}`\n> **Tổng:** `{total}` item",
        "en": "> **Account:** `{account}`\n> **Category:** `{category}`\n> **Total:** `{total}` item(s)",
    },
    "inv_no_items": {
        "vi": "Không tìm thấy item nào trong danh mục này.",
        "en": "No items found in this category.",
    },
    "inv_error_no_data": {
        "vi": "Không lấy được dữ liệu Inventory từ Riot.",
        "en": "Could not retrieve Inventory data from Riot.",
    },
    "inv_error_all_regions_failed": {
        "vi": "Kết nối tới Riot đang không ổn định ở mọi vùng. Vui lòng thử lại sau ít phút.",
        "en": "Could not reach Riot inventory service in any region. Please try again in a few minutes.",
    },
    "inv_page": {
        "vi": "Trang {current}/{total}",
        "en": "Page {current}/{total}",
    },
    "inv_cat_skins": {
        "vi": "Skins",
        "en": "Skins",
    },
    "inv_cat_agents": {
        "vi": "Agents",
        "en": "Agents",
    },
    "inv_cat_buddies": {
        "vi": "Buddies",
        "en": "Buddies",
    },
    "inv_cat_cards": {
        "vi": "Cards",
        "en": "Cards",
    },
    "inv_cat_sprays": {
        "vi": "Sprays",
        "en": "Sprays",
    },
    "inv_cat_titles": {
        "vi": "Titles",
        "en": "Titles",
    },
    "inv_loading": {
        "vi": "Đang tải kho đồ",
        "en": "Loading inventory",
    },
    "inv_all_weapons": {
        "vi": "Tất cả vũ khí",
        "en": "All Weapons",
    },
    "inv_weapon_placeholder": {
        "vi": "Lọc theo vũ khí...",
        "en": "Filter by weapon...",
    },

    "title_daily_shop": {
        "vi": "Daily Shop",
        "en": "Daily Shop",
    },
    "title_night_market": {
        "vi": "🌙 CHỢ ĐÊM",
        "en": "🌙 NIGHT MARKET",
    },
    "title_valorant_tracker": {
        "vi": "📊 VALORANT TRACKER",
        "en": "📊 VALORANT TRACKER",
    },
    "title_valorant_store": {
        "vi": "Daily Shop",
        "en": "Daily Shop",
    },
    "title_match_history": {
        "vi": "Lịch sử trận đấu",
        "en": "Match history",
    },
    "title_inventory": {
        "vi": "🎒 KHO ĐỒ VALORANT",
        "en": "🎒 VALORANT INVENTORY",
    },
    "no_data": {
        "vi": "Không có dữ liệu",
        "en": "No Data",
    },
    "stat_loading": {
        "vi": "Đang tra cứu người chơi",
        "en": "Looking up player",
    },
    "shop_loading": {
        "vi": "Đang tải cửa hàng",
        "en": "Loading shop",
    },
    "loading_hint": {
        "vi": "Vui lòng chờ trong giây lát.",
        "en": "Please wait a moment.",
    },
    "timeout_expired": {
        "vi": "Phiên tương tác đã hết hạn. Hãy chạy lại lệnh để tiếp tục nhé.",
        "en": "This interaction has expired. Please run the command again to continue.",
    },
    "shop_refreshing": {
        "vi": "Đang cập nhật...",
        "en": "Refreshing...",
    },
    "btn_profile": {
        "vi": "Hồ sơ",
        "en": "Profile",
    },
    "btn_match_history": {
        "vi": "Lịch sử trận",
        "en": "Match History",
    },
    "btn_lookup": {
        "vi": "TRA CỨU",
        "en": "LOOK UP",
    },
    "mode_daily_shop": {
        "vi": "cửa hàng hôm nay của bạn",
        "en": "Daily Shop",
    },
    "mode_night_market": {
        "vi": "Night Market của bạn",
        "en": "Night Market",
    },
    "stat_modal_name_ph": {
        "vi": "VD: TenZ",
        "en": "e.g. TenZ",
    },
    "stat_modal_tag_ph": {
        "vi": "VD: SEN",
        "en": "e.g. SEN",
    },
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(lang, entry.get(DEFAULT_LANG, key))
    if kwargs:
        return text.format(**kwargs)
    return text
