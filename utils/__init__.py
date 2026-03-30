import asyncio
import logging
import ssl
from typing import Dict, List, Optional, Tuple, Any

import aiohttp
import certifi

from utils.riot_auth import RiotAuth, AuthResult
from utils.henrik_api import HenrikAPI
from utils.valorant_assets import ValorantAssets
from utils.user_manager import UserManager
from utils.constants import RANK_TIERS, RANK_ICON_BASE, DEFAULT_RANK_ICON, ITEM_TYPE_IDS

logger = logging.getLogger('ValorantAPI')


class ValorantAPI:
    """
    Main Facade for Valorant APIs.
    Composes specialized modules for Auth, Assets, and HenrikDev APIs.
    """

    _ssl_ctx: Optional[ssl.SSLContext] = None

    @classmethod
    def _get_ssl_ctx(cls) -> ssl.SSLContext:
        if cls._ssl_ctx is None:
            cls._ssl_ctx = ssl.create_default_context(cafile=certifi.where())
        return cls._ssl_ctx

    def __init__(self) -> None:
        self.auth = RiotAuth()
        self.henrik = HenrikAPI()
        self.assets = ValorantAssets()
        self.user_manager = UserManager()
        self.session: Optional[aiohttp.ClientSession] = None
        self._session_lock = asyncio.Lock()

    @property
    def region(self) -> str:
        return self.henrik.region

    async def init_session(self) -> aiohttp.ClientSession:
        """Initialize ClientSession and prefetch global data"""
        async with self._session_lock:
            if not self.session or self.session.closed:
                connector = aiohttp.TCPConnector(ssl=self._get_ssl_ctx())
                # Allow outbound API requests to use HTTP(S)_PROXY when present.
                self.session = aiohttp.ClientSession(connector=connector, trust_env=True)
                await self.user_manager.load()
                await self.assets.load_price_data()
                try:
                    await asyncio.wait_for(self.assets.fetch_all_data(self.session), timeout=30.0)
                except asyncio.TimeoutError:
                    logger.error("fetch_all_data() timed out after 30s — skin cache may be empty")
        return self.session

    async def _refresh_loop(self) -> None:
        """Refresh skin asset cache every 24 hours in the background."""
        while True:
            await asyncio.sleep(86400)
            if self.session and not self.session.closed:
                logger.info("Refreshing Valorant asset cache...")
                try:
                    await asyncio.wait_for(self.assets.fetch_all_data(self.session), timeout=30.0)
                    logger.info("Asset cache refreshed successfully.")
                except asyncio.TimeoutError:
                    logger.error("Asset cache refresh timed out after 30s")

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
        await self.user_manager.close()

    def get_auth_link(self) -> str:
        return self.auth.get_auth_link()

    async def auth_with_url(self, url: str, lang: str = "en") -> Tuple[bool, str, Optional[AuthResult]]:
        if not self.session:
            await self.init_session()
        return await self.auth.auth_with_url(url, self.session, lang=lang)

    async def get_stats(self, name: str, tag: str, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.session:
            await self.init_session()
        return await self.henrik.get_stats(name, tag, self.session, region=region)

    async def get_account_info(self, name: str, tag: str) -> Optional[Dict[str, Any]]:
        if not self.session:
            await self.init_session()
        return await self.henrik.get_account_info(name, tag, self.session)

    async def get_recent_matches(self, name: str, tag: str, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.session:
            await self.init_session()
        return await self.henrik.get_recent_matches(name, tag, self.session, region=region)

    async def _get_storefront(self, auth: AuthResult, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch the full storefront data from Riot API."""
        if not self.session:
            await self.init_session()
        target_region = region or self.region
        url = f"https://pd.{target_region}.a.pvp.net/store/v3/storefront/{auth.puuid}"
        try:
            async with self.session.post(url, headers=auth.headers, json={}) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"Storefront API Error {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"Failed to get storefront: {e}")
        return None

    async def get_shop(self, auth: AuthResult, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch user's daily shop storefront"""
        data = await self._get_storefront(auth, region)
        return data.get('SkinsPanelLayout', {}) if data else None

    async def get_nightmarket(self, auth: AuthResult, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch user's Night Market (BonusStore)"""
        data = await self._get_storefront(auth, region)
        return data.get('BonusStore', {}) if data else None

    async def get_inventory(self, auth: AuthResult, item_type: str, region: Optional[str] = None) -> Optional[List]:
        """Fetch player-owned items by category from the entitlements endpoint."""
        if not self.session:
            await self.init_session()
        type_id = ITEM_TYPE_IDS.get(item_type)
        if not type_id:
            logger.error(f"Unknown item type: {item_type}")
            return []

        # Shard mapping for official Riot endpoints
        target_region = (region or self.region).lower()
        shard = target_region
        if target_region in ["latam", "br"]:
            shard = "na"

        url = f"https://pd.{shard}.a.pvp.net/store/v1/entitlements/{auth.puuid}/{type_id}"
        logger.info(f"Fetching inventory from: {url}")
        
        try:
            async with self.session.get(url, headers=auth.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Riot dynamic response structure:
                    # 1. Direct 'Entitlements' list (when ItemTypeID is in URL)
                    # 2. 'EntitlementsByTypes' (fallback or unfiltered)
                    items_raw = data.get("Entitlements", [])
                    if not items_raw:
                        ebt = data.get("EntitlementsByTypes", [])
                        if ebt:
                            items_raw = ebt[0].get("Entitlements", [])
                    
                    if items_raw:
                        items = [e["ItemID"] for e in items_raw]
                        logger.info(f"Successfully fetched {len(items)} items for {item_type}")
                        return items
                        
                    return []
                
                error_text = await resp.text()
                logger.error(f"Inventory API Error {resp.status} for {url}: {error_text}")
        except Exception as e:
            logger.error(f"Failed to get inventory ({item_type}) at {url}: {e}")
        return None

    async def resolve_region(self, auth: AuthResult) -> str:
        """Resolve player region from account info, fallback to default region."""
        acc_data = await self.get_account_info(auth.game_name, auth.tag_line)
        if acc_data and acc_data.get('status') == 200:
            return str(acc_data.get('data', {}).get('region', '')).lower() or self.region
        return self.region

    async def get_skin_details(self, level_uuid: str) -> Optional[Dict[str, Any]]:
        if not self.session:
            await self.init_session()
        return await self.assets.get_skin_details(level_uuid, self.session)

    def get_rarity_info(self, rarity_uuid: Optional[str]) -> Dict[str, Any]:
        return self.assets.get_rarity_info(rarity_uuid)

    def get_rarity_icon(self, rarity_uuid: Optional[str]) -> Optional[str]:
        return self.assets.get_rarity_icon(rarity_uuid)

    def get_hardcoded_price(self, rarity_uuid: Optional[str], is_melee: bool = False, level_uuid: Optional[str] = None) -> int:
        return self.assets.get_hardcoded_price(rarity_uuid, is_melee, level_uuid)

    def is_melee_weapon(self, weapon_type: str, skin_name: str) -> bool:
        return self.assets.is_melee_weapon(weapon_type, skin_name)

    async def link_user(self, discord_id: int, name: str, tag: str, region: str) -> bool:
        return await self.user_manager.link_user(discord_id, name, tag, region)

    async def get_user_link(self, discord_id: int) -> Optional[Tuple[str, str, Optional[str]]]:
        return await self.user_manager.get_user_link(discord_id)

    async def unlink_user(self, discord_id: int) -> bool:
        return await self.user_manager.unlink_user(discord_id)

    async def get_language(self, discord_id: int) -> str:
        return await self.user_manager.get_language(discord_id)

    async def set_language(self, discord_id: int, lang: str) -> bool:
        return await self.user_manager.set_language(discord_id, lang)

    def get_rank_assets(self, rank_name: str) -> Tuple[int, str]:
        """Get color and icon URL for a specific rank with correct tier handling"""
        rank_name = rank_name.lower()
        color = 0x2b2d31
        icon = DEFAULT_RANK_ICON

        for r, (c, base_idx) in RANK_TIERS.items():
            if r in rank_name:
                color = c
                offset = 0
                if " 2" in rank_name: offset = 1
                elif " 3" in rank_name: offset = 2

                if r == "radiant": offset = 0

                icon = f"{RANK_ICON_BASE}/{base_idx + offset}/largeicon.png"
                break
        return color, icon
