# UX Review Report — inu-bot

**Date:** 2026-03-30
**Scope:** `views/`, `cogs/`, `utils/i18n.py` — Discord embed design, interaction flow, button/modal UX

---

## Summary

| Category | Critical | High | Medium | Low |
|---|---|---|---|---|
| Loading states | 1 | — | — | — |
| Error messages | — | 1 | 2 | — |
| Interaction flow | — | 2 | 1 | — |
| Button/Modal UX | — | 1 | 2 | 1 |
| Embed design | — | — | 2 | 2 |
| i18n | — | — | 1 | 2 |
| Discord-specific | — | 1 | 1 | 1 |

---

## CRITICAL

### 1. Loading indicator không có thông tin

**Files:** `views/shop_views.py:52-53`, `views/inventory_views.py:72-78`, `views/stat_views.py:70`

```python
# Hiện tại — chỉ có text
loading_embed = discord.Embed(description=f"**{t('shop_loading', self.lang)}**", color=EMBED_COLOR)

# Tốt hơn
loading_embed = discord.Embed(
    description=f"🔄 **{t('shop_loading', self.lang)}**\n{t('shop_loading_hint', self.lang)}",
    color=EMBED_COLOR
)
```

User không biết bot đang làm gì (fetching auth → fetching shop → building embeds), chờ bao lâu, hay đã bị stuck. Nhất là inventory có thể retry 5 region mất 10–50 giây.

**Fix:** Thêm emoji `🔄`, thêm 1 dòng hint ngắn vào i18n (`"Thường mất 2–5 giây"`).

---

## HIGH

### 2. Timeout buttons im lặng — user bị stuck

**File:** `views/base_views.py:13-22`

Khi timeout (5 phút cho shop/inventory, 2 phút cho stat/help), `on_timeout()` disable buttons nhưng không gửi thông báo nào. User thấy buttons mờ, không hiểu tại sao, nghĩ bot bị lỗi.

```python
# Hiện tại — silent disable
async def on_timeout(self) -> None:
    for item in self.children:
        ...disable...
    if self.message:
        await self.message.edit(view=self)

# Cần thêm — notify user
async def on_timeout(self) -> None:
    # ... disable buttons ...
    if self.message:
        try:
            await self.message.edit(view=self)
            await self.message.reply(
                t("timeout_expired", ???),  # cần lang
                mention_author=False
            )
        except (discord.NotFound, discord.HTTPException):
            pass
```

**Vấn đề thứ 2:** `BaseView` không lưu `lang`, nên không thể gọi `t()` trong `on_timeout()`. Cần pass `lang` vào `BaseView.__init__`.

---

### 3. Multi-region retry — silent failure khi tất cả region fail

**File:** `views/inventory_views.py:88-103`

```python
for s in shards_to_try:
    try:
        item_ids = await asyncio.wait_for(
            self.api.get_inventory(auth, "skins", region=s), timeout=10.0
        )
    except asyncio.TimeoutError:
        continue
    if item_ids is not None:
        final_region = s
        break

if not item_ids:  # BUG: cả "no skins" lẫn "tất cả region lỗi" đều vào đây
    # Error embed giống nhau
```

Nếu tất cả 5 regions đều timeout hoặc trả `None`, `item_ids` sẽ là `None` (từ lần retry cuối), nhưng flow đi vào `if not item_ids:` cùng đường với trường hợp user thực sự không có skin. User không biết là lỗi mạng hay inventory thật sự trống.

**Fix:**
```python
all_failed = True
for s in shards_to_try:
    ...
    if item_ids is not None:
        all_failed = False
        break

if all_failed:
    # Lỗi kết nối — cần retry khác với empty inventory
    ...
elif not item_ids:
    # Thực sự không có skin
    ...
```

---

### 4. Intro message không xóa khi buttons expire

**File:** `views/shop_views.py:35-43`, `views/inventory_views.py:52-60`

Nếu user mở modal và **nhấn X đóng modal** mà không submit, hoặc timeout xảy ra trước khi submit, `intro_message` cleanup chỉ chạy trong `on_submit`. Buttons intro vẫn còn active — user có thể mở modal lại (không gây lỗi nhưng confusing).

---

## MEDIUM

### 5. Error embed format không nhất quán

So sánh giữa 3 features:

| Feature | Has title? | Color | Source |
|---|---|---|---|
| Shop auth error | ❌ | `ERROR_COLOR` | `shop_views.py:43` |
| Shop no skins | ❌ | `ERROR_COLOR` | `shop_views.py:91` |
| Inventory no data | ✅ `"INVENTORY"` (hardcoded!) | `ERROR_COLOR` | `inventory_views.py:103` |
| Stat account error | ❌ | `0xff4444` (hardcoded) | `stat_views.py:108` |
| Stat rank error | ❌ | `0xff4444` (hardcoded) | `stat_views.py:134` |

**Hai vấn đề:**
1. `stat_views.py` vẫn dùng `0xff4444` hardcode thay vì import `ERROR_COLOR`
2. `inventory_views.py:103` — `title="INVENTORY"` không qua `t()` → không dịch sang tiếng Việt

**Fix:**
```python
# stat_views.py — import và dùng ERROR_COLOR
from utils.constants import ERROR_COLOR

# inventory_views.py:103
discord.Embed(title=t("title_inventory", self.lang), description=..., color=ERROR_COLOR)
```

---

### 6. Shop skin embed thiếu thông tin context

**File:** `views/shop_views.py:151-177`

Skin embed chỉ có: author (tên skin), thumbnail (ảnh), footer (giá VP).
Không có: loại vũ khí, tên tier/rarity (chỉ dùng màu).

So với Inventory (`views/inventory_views.py:326-346`) có footer hiển thị tier name (Select, Deluxe, Premium...).

**Fix:** Thêm `weapon_type` vào footer hoặc body:
```python
# Sau dòng set_footer
if weapon_type:
    embed.set_footer(text=f"{price_text} • {weapon_type}", icon_url=VP_ICON_URL)
```

---

### 7. Hardcoded strings tiếng Anh không qua i18n

**Files:** `views/inventory_views.py:69,104`

```python
# inventory_views.py:69 — không dịch
loading_embed = discord.Embed(title="INVENTORY", ...)

# inventory_views.py:104 — không dịch
error_embed = discord.Embed(title="INVENTORY", ...)
```

`t("title_inventory", lang)` đã có trong `i18n.py:493-495`. Chỉ cần dùng.

**File:** `views/stat_views.py:175, 280`

```python
# Hardcoded không qua i18n
profile_embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url=rank_icon)
matches_embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url=rank_icon)
```

`t("footer", lang)` đã có trong `i18n.py:90-94`. Không dùng.

---

### 8. Embed title format không nhất quán

| Feature | Title format | Example |
|---|---|---|
| Shop | String từ i18n | "Cửa Hàng Hàng Ngày" |
| Inventory | `{emoji} INVENTORY — {category}` | "🔫 INVENTORY — SKINS" |
| Stats | `{name}#{tag}` | "TenZ#SEN" |
| Help | String từ i18n | "Inu Bot — Help" |

Shop và Stats không có emoji prefix, Inventory luôn có. Chưa thống nhất visual identity.

---

## LOW

### 9. Button labels thiếu emoji

**Files:** `views/shop_views.py:190-194`, `views/inventory_views.py:369-380`

```python
# Hiện tại — không có emoji
discord.ui.Button(label=t("btn_login", lang), style=discord.ButtonStyle.link, url=auth_url)
discord.ui.Button(label=t("btn_paste", lang), style=discord.ButtonStyle.success)

# i18n.py:84-90
"btn_login": {"vi": "Đăng nhập Riot", "en": "Sign in to Riot"},
"btn_paste": {"vi": "Dán Link vào đây", "en": "Paste Link Here"},
```

Không có visual indicator phân biệt hai nút. Nên thêm emoji vào i18n strings:
- `"btn_login"` → `"🔑 Đăng nhập Riot"` / `"🔑 Sign in to Riot"`
- `"btn_paste"` → `"📋 Dán Link vào đây"` / `"📋 Paste Link Here"`

---

### 10. Footer attribution không nhất quán

| Location | Footer text |
|---|---|
| `stat_views.py:175` | `"Inu Bot • Powered by HenrikDev API"` (hardcoded) |
| `stat_views.py:280` | `"Inu Bot • Powered by HenrikDev API"` (hardcoded) |
| `shop_views.py:83,119` | `t("footer", lang)` = `"Powered by Inu Bot"` |
| `inventory_views.py:296` | `t("footer", lang)` |
| `info.py:82,92,...` | `"Inu Bot"` (hardcoded, không đề cập API) |

Stats hardcode thêm "Powered by HenrikDev API" mà các feature khác không có. Nên thống nhất qua i18n hoặc thêm constant `STAT_FOOTER`.

---

### 11. `ShopView` timeout quá dài so với auth token lifetime

**File:** `views/shop_views.py:182`

```python
super().__init__(timeout=300)  # 5 phút
```

Riot access token expire sau **3600 giây (1 giờ)** từ link trong redirect URL. Timeout 5 phút là hợp lý về token, nhưng sau 5 phút buttons bị disable, user phải chạy lại lệnh. Không có ghi chú gì cho user biết thời gian còn lại.

---

## Điểm tốt (không cần sửa)

- **Defer-then-edit pattern** — Tất cả modals đều `defer()` ngay lập tức, sau đó `edit_original_response()`. Không spam messages.
- **Owner check** — Tất cả Views đều kiểm tra `interaction.user.id != owner_id` trước khi xử lý.
- **Pagination bounds** — `prev_btn` disabled khi page=0, `next_btn` disabled khi page=last. Reset về page 0 khi đổi filter.
- **Embed count safe** — Max 9 embeds (1 header + 8 skins) trong inventory, dưới giới hạn Discord 10.
- **Ephemeral usage** — Lỗi cá nhân (auth fail, button denied) dùng ephemeral đúng chỗ.
- **i18n coverage** — Không có missing translation keys.
- **No dead-code buttons** — Không có button nào không có callback.

---

## Top 5 ưu tiên fix

| # | Issue | Effort | Impact |
|---|---|---|---|
| 1 | Thêm loading hint text + emoji | Thấp | Cao — giảm user confusion |
| 2 | `BaseView` nhận `lang`, notify khi timeout | Trung bình | Cao — fix dead-end UX |
| 3 | Phân biệt network error vs empty inventory | Thấp | Cao — user hiểu vấn đề |
| 4 | Fix `ERROR_COLOR` và hardcoded strings trong stat/inventory | Thấp | Trung bình — consistency |
| 5 | Thêm emoji vào `btn_login`/`btn_paste` i18n | Thấp | Thấp — visual polish |
