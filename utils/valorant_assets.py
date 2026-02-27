import os
import json
import logging
from typing import Dict, Optional, Any

import aiohttp
import aiofiles

from utils.constants import RARITY_DATA, MELEE_KEYWORDS

logger = logging.getLogger('ValorantAssets')


class ValorantAssets:
    """Manages weapon skin data, rarity metadata, and price lookups."""

    def __init__(self) -> None:
        self.skin_map: Dict[str, Dict[str, Any]] = {}
        self.rarity_map: Dict[str, Dict[str, Any]] = {}
        self.price_overrides: Dict[str, int] = {}
        self.rarity_data: Dict[str, Dict[str, Any]] = dict(RARITY_DATA)

    async def load_price_data(self) -> None:
        """Load hardcoded price data from JSON file"""
        try:
            path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "assets", "skin_prices.json"
            )
            if not os.path.exists(path):
                logger.warning(f"Price data file not found at {path}")
                return

            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)

                for tier_uuid, tier_info in data.get('tiers', {}).items():
                    self.rarity_data[tier_uuid] = {
                        'name': tier_info['name'],
                        'color': tier_info['color'],
                        'gun_price': tier_info.get('gun', 0),
                        'melee_price': tier_info.get('melee', 0)
                    }

                self.price_overrides = data.get('overrides', {})
                logger.info(f"Loaded {len(self.price_overrides)} price overrides.")
        except Exception as e:
            logger.error(f"Failed to load skin price data: {e}")

    async def fetch_all_data(self, session: aiohttp.ClientSession) -> None:
        """Prefetch weapon skins and rarity metadata for faster lookups"""
        try:
            async with session.get("https://valorant-api.com/v1/weapons?language=en-US") as resp:
                data = await resp.json()
                if data.get('status') == 200:
                    for weapon in data.get('data', []):
                        for skin in weapon.get('skins', []):
                            skin_data = {
                                'name': skin['displayName'],
                                'icon': skin.get('displayIcon'),
                                'rarity': skin.get('contentTierUuid'),
                                'weapon': weapon['displayName']
                            }
                            self.skin_map[skin['uuid']] = skin_data

                            for level in skin.get('levels', []):
                                self.skin_map[level['uuid']] = {
                                    'name': skin['displayName'],
                                    'icon': level.get('displayIcon') or skin.get('displayIcon'),
                                    'rarity': skin.get('contentTierUuid'),
                                    'weapon': weapon['displayName']
                                }

            async with session.get("https://valorant-api.com/v1/contenttiers") as resp:
                data = await resp.json()
                if data.get('status') == 200:
                    for tier in data.get('data', []):
                        self.rarity_map[tier['uuid']] = {
                            'name': tier['devName'],
                            'icon': tier['displayIcon']
                        }
        except Exception as e:
            logger.error(f"Error prefetching Valorant data: {e}")

    async def get_skin_details(
        self, level_uuid: str, session: aiohttp.ClientSession
    ) -> Optional[Dict[str, Any]]:
        """Lookup skin details from cache or Valorant-API"""
        if not level_uuid:
            return None

        if level_uuid in self.skin_map:
            return self.skin_map[level_uuid]

        url = f"https://valorant-api.com/v1/weapons/skinlevels/{level_uuid}?language=en-US"
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    raw = data.get('data')
                    if raw:
                        return {
                            'name': raw.get('displayName', 'Unknown Skin'),
                            'icon': raw.get('displayIcon'),
                            'rarity': raw.get('contentTierUuid'),
                            'weapon': raw.get('weapon', '')
                        }
        except Exception as e:
            logger.error(f"Failed to get skin details for {level_uuid}: {e}")
        return None

    def get_rarity_info(self, rarity_uuid: Optional[str]) -> Dict[str, Any]:
        """Get color, name and standard price for a rarity"""
        return self.rarity_data.get(
            rarity_uuid or "",
            {'name': 'Unknown', 'color': 0x2b2d31, 'gun_price': 0, 'melee_price': 0}
        )

    def get_hardcoded_price(
        self,
        rarity_uuid: Optional[str],
        is_melee: bool = False,
        level_uuid: Optional[str] = None
    ) -> int:
        """Get the standard price for a skin rarity, checked against overrides"""
        if level_uuid and level_uuid in self.price_overrides:
            return self.price_overrides[level_uuid]

        info = self.get_rarity_info(rarity_uuid)
        return info.get('melee_price' if is_melee else 'gun_price', 0)

    @staticmethod
    def is_melee_weapon(weapon_type: str, skin_name: str) -> bool:
        """Check if a weapon is a melee type"""
        if weapon_type.lower() == "melee":
            return True
        skin_name_lower = skin_name.lower()
        return any(kw in skin_name_lower for kw in MELEE_KEYWORDS)
