import os
import json
import logging
from typing import Dict, Optional, Any

import aiohttp
import aiofiles
import asyncio

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
            endpoints = {
                "weapons": "https://valorant-api.com/v1/weapons?language=en-US",
                "tiers": "https://valorant-api.com/v1/contenttiers"
            }

            async def fetch(name, url):
                try:
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            return name, await resp.json()
                except Exception as e:
                    logger.error(f"Failed to fetch {name} from {url}: {e}")
                return name, None

            tasks = [fetch(name, url) for name, url in endpoints.items()]
            results = await asyncio.gather(*tasks)

            for name, data in results:
                if not data or data.get('status') != 200:
                    continue
                raw = data.get('data', [])

                if name == "weapons":
                    for weapon in raw:
                        weapon_name = weapon.get('displayName', '')
                        for skin in weapon.get('skins', []):
                            skin_name = skin.get('displayName', 'Unknown Skin')
                            rarity_uuid = skin.get('contentTierUuid')
                            # Use preview-friendly icons only to avoid distorted/cropped full renders in thumbnails.
                            chromas = skin.get('chromas', [])
                            fallback_chroma_icon = None
                            for chroma in chromas:
                                chroma_icon = chroma.get('displayIcon')
                                if chroma_icon:
                                    fallback_chroma_icon = chroma_icon
                                    break
                            skin_icon = skin.get('displayIcon') or fallback_chroma_icon
                            
                            skin_data = {
                                'name': skin_name,
                                'icon': skin_icon,
                                'rarity': rarity_uuid,
                                'weapon': weapon_name
                            }
                            self.skin_map[skin['uuid']] = skin_data
                            for level in skin.get('levels', []):
                                if level['uuid'] not in self.skin_map:
                                    level_icon = level.get('displayIcon') or skin_icon
                                    self.skin_map[level['uuid']] = {
                                        'name': skin_name,
                                        'icon': level_icon,
                                        'rarity': rarity_uuid,
                                        'weapon': weapon_name
                                    }
                            for chroma in chromas:
                                if chroma['uuid'] not in self.skin_map:
                                    self.skin_map[chroma['uuid']] = {
                                        'name': chroma.get('displayName') or skin_name,
                                        'icon': chroma.get('displayIcon') or skin_icon,
                                        'rarity': rarity_uuid,
                                        'weapon': weapon_name
                                    }
                elif name == "tiers":
                    for tier in raw:
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
                        result = {
                            'name': raw.get('displayName', 'Unknown Skin'),
                            # Keep thumbnails on stable icon assets; fullRender often crops poorly in Discord.
                            'icon': raw.get('displayIcon'),
                            'rarity': raw.get('contentTierUuid'),
                            'weapon': raw.get('weapon', '')
                        }
                        self.skin_map[level_uuid] = result
                        return result
        except Exception as e:
            logger.error(f"Failed to get skin details for {level_uuid}: {e}")
        return None

    def get_rarity_info(self, rarity_uuid: Optional[str]) -> Dict[str, Any]:
        """Get color, name and standard price for a rarity"""
        default = {'name': 'Unknown', 'color': 0x2b2d31, 'gun_price': 0, 'melee_price': 0}
        if not rarity_uuid:
            return default
        info = self.rarity_data.get(rarity_uuid)
        if info is None:
            logger.debug(f"Unknown rarity UUID: {rarity_uuid}")
            return default
        return info

    def get_rarity_icon(self, rarity_uuid: Optional[str]) -> Optional[str]:
        """Get the display icon URL for a content tier"""
        if not rarity_uuid:
            return None
        tier = self.rarity_map.get(rarity_uuid)
        return tier.get('icon') if tier else None

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
