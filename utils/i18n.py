from typing import Any, Dict, Union

DEFAULT_LANG = "en"

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
        "vi": "Xác thực Cửa Hàng",
        "en": "STORE Authentication",
    },
    "nm_modal_title": {
        "vi": "Xác thực Night Market",
        "en": "NIGHT MARKET Authentication",
    },
    "shop_modal_label": {
        "vi": "Dán link Redirect vào đây",
        "en": "Paste the Redirect link here",
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
        "vi": "🔑 Đăng nhập Riot",
        "en": "🔑 Sign in to Riot",
    },
    "btn_paste": {
        "vi": "📋 Dán Link",
        "en": "📋 Paste Link",
    },
    "footer": {
        "vi": "Inu Bot",
        "en": "Powered by Inu Bot",
    },
    "shop_intro": {
        "vi": (
            "Để xem **{mode}**, hãy làm 3 bước:\n\n"
            "1️⃣ Nhấn **Đăng nhập Riot** → đăng nhập tài khoản\n"
            "2️⃣ Sau khi chuyển hướng, **copy toàn bộ URL** trên thanh địa chỉ\n"
            "3️⃣ Nhấn **Dán Link** → paste URL vừa copy\n\n"
            "⏱️ Nút sẽ hết hạn sau 5 phút, chạy lại lệnh nếu quá hạn.\n\n"
            "*Dùng `/safety` để tìm hiểu về bảo mật.*"
        ),
        "en": (
            "To view your **{mode}**, follow 3 steps:\n\n"
            "1️⃣ Click **Sign in to Riot** → sign in to your account\n"
            "2️⃣ After redirect, **copy the entire URL** from the address bar\n"
            "3️⃣ Click **Paste Link** → paste the URL you copied\n\n"
            "⏱️ Buttons expire after 5 minutes, run the command again when needed.\n\n"
            "*Use `/safety` to learn more about security.*"
        ),
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

    "help_title": {
        "vi": "Inu Bot",
        "en": "Inu Bot",
    },
    "help_desc": {
        "vi": (
            "v1.1.0 · Valorant companion\n\n"
            "Tra cứu stat, Daily Shop, Night Market và Inventory của bạn."
        ),
        "en": (
            "v1.1.0 · Valorant companion\n\n"
            "Track stats, Daily Shop, Night Market and your Inventory."
        ),
    },
    "help_category_label": {
        "vi": "DANH MỤC",
        "en": "CATEGORIES",
    },
    "help_stat_label": {
        "vi": "Stat",
        "en": "Stat",
    },
    "help_stat_sub": {
        "vi": "Rank, RR, lịch sử trận đấu",
        "en": "Rank, RR, match history",
    },
    "help_shop_label": {
        "vi": "Shop",
        "en": "Shop",
    },
    "help_shop_sub": {
        "vi": "Daily Shop · Night Market",
        "en": "Daily Shop · Night Market",
    },
    "help_inv_label": {
        "vi": "Inventory",
        "en": "Inventory",
    },
    "help_inv_sub": {
        "vi": "Kho skin súng của bạn",
        "en": "Your gun skin collection",
    },
    "help_misc_label": {
        "vi": "Misc",
        "en": "Misc",
    },
    "help_misc_sub": {
        "vi": "Prefix, hỗ trợ, cập nhật",
        "en": "Prefix, support, updates",
    },
    "help_stat_title": {
        "vi": "HƯỚNG DẪN — STAT",
        "en": "GUIDE — STAT",
    },
    "help_stat_desc": {
        "vi": (
            "Tra cứu stat Valorant theo nhiều cách.\n\n"
            "```\n"
            "/stat              Tra cứu nhanh (đã link)\n"
            "/stat user:@abc    Xem stat người khác\n"
            "/stat name:X tag:Y Tra cứu bằng Riot ID\n"
            "```\n\n"
            "**Liên kết tài khoản**\n"
            "```\n"
            "/link name tag     Liên kết Riot ID\n"
            "/unlink            Hủy liên kết\n"
            "```\n"
            "Link xong thì gõ `/stat` là xem được luôn."
        ),
        "en": (
            "Look up Valorant stats in multiple ways.\n\n"
            "```\n"
            "/stat              Quick lookup (if linked)\n"
            "/stat user:@abc    View another user's stats\n"
            "/stat name:X tag:Y Manual lookup by Riot ID\n"
            "```\n\n"
            "**Account Linking**\n"
            "```\n"
            "/link name tag     Link Riot ID to Discord\n"
            "/unlink            Unlink account\n"
            "```\n"
            "After linking, just type `/stat` to view your stats instantly."
        ),
    },
    "help_shop_title": {
        "vi": "HƯỚNG DẪN — SHOP",
        "en": "GUIDE — SHOP",
    },
    "help_shop_desc": {
        "vi": (
            "Xem Daily Shop và Night Market.\n\n"
            "```\n"
            "/shop              Xem cửa hàng\n"
            "/nightmarket       Xem Night Market\n"
            "/safety            Giải thích bảo mật\n"
            "```\n\n"
            "**Cách dùng**\n"
            "1. Gõ `/shop` hoặc `/nightmarket`\n"
            "2. Nhấn nút đăng nhập Riot\n"
            "3. Đăng nhập trên trang chính thức\n"
            "4. Copy toàn bộ URL redirect\n"
            "5. Dán link vào modal\n\n"
            "Token chỉ dùng 1 lần, không lưu trữ."
        ),
        "en": (
            "View your Daily Shop and Night Market.\n\n"
            "```\n"
            "/shop              View Daily Shop\n"
            "/nightmarket       View Night Market\n"
            "/safety            Security explanation\n"
            "```\n\n"
            "**How to use**\n"
            "1. Type `/shop` or `/nightmarket`\n"
            "2. Click the Riot sign-in button\n"
            "3. Sign in on the official website\n"
            "4. Copy the entire redirect URL\n"
            "5. Paste the link into the modal\n\n"
            "Tokens are used once and never stored."
        ),
    },
    "help_inv_title": {
        "vi": "HƯỚNG DẪN — INVENTORY",
        "en": "GUIDE — INVENTORY",
    },
    "help_inv_desc": {
        "vi": (
            "Xem kho đồ skin súng bạn đang sở hữu.\n\n"
            "```\n"
            "/inventory         Xem kho đồ skin\n"
            "```\n\n"
            "**Tính năng**\n"
            "- Hiển thị danh sách skin súng của bạn\n"
            "- Có menu lọc theo loại súng (Vandal, Phantom, v.v.)\n"
            "- Hiển thị hình ảnh, tên và độ hiếm skin\n\n"
            "**Cách dùng**\n"
            "Tương tự như `/shop`, bạn cần đăng nhập Riot để bot lấy dữ liệu (Access Token chỉ dùng 1 lần)."
        ),
        "en": (
            "View your collection of owned weapon skins.\n\n"
            "```\n"
            "/inventory         View skin inventory\n"
            "```\n\n"
            "**Features**\n"
            "- List your owned weapon skins\n"
            "- Filter by weapon type (Vandal, Phantom, etc.)\n"
            "- Shows skin image, name, and rarity\n\n"
            "**How to use**\n"
            "Similar to `/shop`, you need to sign in to Riot (Access Token is one-time use)."
        ),
    },
    "help_misc_title": {
        "vi": "HƯỚNG DẪN — KHÁC",
        "en": "GUIDE — MISC",
    },
    "help_misc_desc": {
        "vi": (
            "Các lệnh tiện ích khác.\n\n"
            "```\n"
            "/help              Menu hướng dẫn\n"
            "/update            Xem cập nhật mới nhất\n"
            "/language          Đổi ngôn ngữ\n"
            "```\n\n"
            "**Prefix**\n"
            "Tất cả lệnh đều dùng được với prefix `!`\n"
            "Ví dụ: `!stat`, `!shop`, `!help`\n\n"
            "**Hỗ trợ**\n"
            "Gặp lỗi thì thử lại sau vài giây nhé.\n"
            "Bot phụ thuộc API bên ngoài nên đôi khi "
            "có thể bị chậm hoặc gián đoạn."
        ),
        "en": (
            "Other utility commands.\n\n"
            "```\n"
            "/help              Open this guide menu\n"
            "/update            View latest updates\n"
            "/language          Change language\n"
            "```\n\n"
            "**Prefix**\n"
            "All commands also support the `!` prefix\n"
            "Example: `!stat`, `!shop`, `!help`\n\n"
            "**Support**\n"
            "If you encounter an error, try again after a few seconds.\n"
            "The bot relies on external APIs, so occasional "
            "slowdowns or interruptions may occur."
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
        "vi": "Đang tải inventory...",
        "en": "Loading inventory...",
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
        "vi": "🛒 CỬA HÀNG HÀNG NGÀY",
        "en": "🛒 DAILY SHOP",
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
        "vi": "🛍️ CỬA HÀNG VALORANT",
        "en": "🛍️ VALORANT STORE",
    },
    "title_match_history": {
        "vi": "LỊCH SỬ TRẬN ĐẤU — {name}#{tag}",
        "en": "MATCH HISTORY — {name}#{tag}",
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
        "vi": "Đang tra cứu...",
        "en": "Looking up stats...",
    },
    "shop_loading": {
        "vi": "Đang tải...",
        "en": "Loading...",
    },
    "shop_loading_hint": {
        "vi": "Thường mất 2-5 giây.",
        "en": "Usually takes 2-5 seconds.",
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
        "vi": "Cửa Hàng",
        "en": "Daily Shop",
    },
    "mode_night_market": {
        "vi": "Chợ Đêm",
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
