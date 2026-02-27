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
        "vi": "> **Tài khoản:** `{account}`\n> **Làm mới sau:** `{time}`",
        "en": "> **Account:** `{account}`\n> **Refreshes in:** `{time}`",
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
        "vi": "> **Tài khoản:** `{account}`\n> **Kết thúc sau:** `{time}`",
        "en": "> **Account:** `{account}`\n> **Ends in:** `{time}`",
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
        "vi": "1. Đăng nhập Riot",
        "en": "1. Sign in to Riot",
    },
    "btn_paste": {
        "vi": "2. Dán Link vào đây",
        "en": "2. Paste Link Here",
    },
    "footer": {
        "vi": "Inu Bot",
        "en": "Powered by Inu Bot",
    },
    "shop_intro": {
        "vi": (
            "Làm theo các bước sau để xem **{mode}** nhé:\n\n"
            "> **1.** Nhấn nút **`1. Đăng nhập Riot`** bên dưới.\n"
            "> **2.** Đăng nhập tài khoản Riot Games.\n"
            "> **3.** Chờ trang web chuyển hướng (có thể hiện trang trắng).\n"
            "> **4.** **Copy toàn bộ URL** trên thanh địa chỉ.\n"
            "> **5.** Quay lại đây, nhấn **`2. Dán Link vào đây`** và gửi link.\n\n"
            "*Dùng `/safety` để tìm hiểu về bảo mật tài khoản.*"
        ),
        "en": (
            "Please follow these steps to view your **{mode}**:\n\n"
            "> **1.** Click the **`1. Sign in to Riot`** button below.\n"
            "> **2.** Sign in to your Riot Games account.\n"
            "> **3.** Wait for the page to redirect (it may show a blank page or an error).\n"
            "> **4.** **Copy the entire URL** from the address bar.\n"
            "> **5.** Come back here, click **`2. Paste Link Here`** and submit the link.\n\n"
            "*Use `/safety` to learn more about account security.*"
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
        "vi": "HƯỚNG DẪN SỬ DỤNG",
        "en": "USER GUIDE",
    },
    "help_desc": {
        "vi": (
            "Inu Bot giúp bạn tra cứu stat Valorant, "
            "xem Daily Shop và Night Market.\n\n"
            "Chọn một mục bên dưới để xem chi tiết.\n\n"
            "```\n"
            "Stat        Rank, RR, lịch sử trận đấu\n"
            "Shop        Cửa hàng, Night Market\n"
            "Misc        Prefix, hỗ trợ, cập nhật\n"
            "```"
        ),
        "en": (
            "Inu Bot helps you look up Valorant stats, "
            "view your Daily Shop and Night Market.\n\n"
            "Select a category below for details.\n\n"
            "```\n"
            "Stat        Rank, RR, match history lookup\n"
            "Shop        Daily shop, night market viewer\n"
            "Misc        Prefix, support, updates\n"
            "```"
        ),
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
}


def t(key: str, lang: str = DEFAULT_LANG, **kwargs: Any) -> str:
    entry = STRINGS.get(key)
    if not entry:
        return key
    text = entry.get(lang, entry.get(DEFAULT_LANG, key))
    if kwargs:
        return text.format(**kwargs)
    return text
