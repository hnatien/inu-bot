from typing import Dict, List, Any



VP_ICON_URL: str = (
    "https://media.valorant-api.com/currencies/"
    "85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/displayicon.png"
)

RARITY_DATA: Dict[str, Dict[str, Any]] = {
    '12683d76-48d7-84a3-4e09-6985794f0445': {
        'name': 'Select', 'color': 0x5a9fe2,
        'gun_price': 875, 'melee_price': 1750
    },
    '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {
        'name': 'Deluxe', 'color': 0x009587,
        'gun_price': 1275, 'melee_price': 2550
    },
    '60bca009-4182-7998-dee7-b8a2558dc369': {
        'name': 'Premium', 'color': 0xd1548d,
        'gun_price': 1775, 'melee_price': 3550
    },
    'e046854e-406c-37f4-6607-19a9ba8426fc': {
        'name': 'Exclusive', 'color': 0xf5955b,
        'gun_price': 2175, 'melee_price': 4350
    },
    '411e4a55-4e59-7757-41f0-86a53f101bb5': {
        'name': 'Ultra', 'color': 0xfad663,
        'gun_price': 2475, 'melee_price': 4950
    }
}

MELEE_KEYWORDS: List[str] = [
    "knife", "karambit", "butterfly", "axe", "blade", "hammer",
    "dagger", "fan", "bat", "scythe", "gauntlet", "stiletto", "crowbar"
]

RANK_TIERS: Dict[str, tuple] = {
    "iron": (0x565656, 3),
    "bronze": (0x8c7857, 6),
    "silver": (0xc0c0c0, 9),
    "gold": (0xffd700, 12),
    "platinum": (0x3e8ca7, 15),
    "diamond": (0xb48bd6, 18),
    "ascendant": (0x62a67e, 21),
    "immortal": (0xbf3650, 24),
    "radiant": (0xffffaa, 27),
}

RANK_ICON_BASE: str = (
    "https://media.valorant-api.com/competitivetiers/"
    "03621f52-342b-cf4e-4f86-9350a49c6d04"
)

DEFAULT_RANK_ICON: str = f"{RANK_ICON_BASE}/0/largeicon.png"

ITEM_TYPE_IDS: Dict[str, str] = {
    "skins": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
    "agents": "01bb38e1-da47-4e6a-9b3d-945fe4655707",
    "buddies": "dd3bf334-87f3-40bd-b043-682a57a8dc3a",
    "cards": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
    "sprays": "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475",
    "titles": "de7caa6b-adf7-4588-bbd1-143831e786c6",
}

INVENTORY_ITEMS_PER_PAGE: int = 8
