import logging
import ssl
from typing import Dict, Optional, Tuple, Any

import aiohttp
import certifi

from utils.riot_auth import RiotAuth
from utils.henrik_api import HenrikAPI
from utils.valorant_assets import ValorantAssets
from utils.user_manager import UserManager
from utils.constants import RANK_TIERS, RANK_ICON_BASE, DEFAULT_RANK_ICON

logger = logging.getLogger('ValorantAPI')


class ValorantAPI:
    """
    Main Facade for Valorant APIs.
    Composes specialized modules for Auth, Assets, and HenrikDev APIs.
    """

    def __init__(self) -> None:
        self.auth = RiotAuth()
        self.henrik = HenrikAPI()
        self.assets = ValorantAssets()
        self.user_manager = UserManager()
        
        self.session: Optional[aiohttp.ClientSession] = None

    @property
    def headers(self) -> Dict[str, str]:
        return self.auth.headers

    @property
    def puuid(self) -> str:
        return self.auth.puuid

    @property
    def game_name(self) -> str:
        return self.auth.game_name
    
    @property
    def tag_line(self) -> str:
        return self.auth.tag_line

    @property
    def region(self) -> str:
        return self.henrik.region

    @property
    def VP_ICON_URL(self) -> str:
        from utils.constants import VP_ICON_URL
        return VP_ICON_URL

    async def init_session(self) -> aiohttp.ClientSession:
        """Initialize ClientSession and prefetch global data"""
        if not self.session:
            ssl_ctx = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_ctx)
            self.session = aiohttp.ClientSession(connector=connector)
            
            await self.user_manager.load()
            await self.assets.load_price_data()
            await self.assets.fetch_all_data(self.session)
        return self.session

    async def close(self) -> None:
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()

    # --- Auth Delegation ---
    def get_auth_link(self) -> str:
        return self.auth.get_auth_link()

    async def auth_with_url(self, url: str) -> Tuple[bool, str]:
        if not self.session: await self.init_session()
        return await self.auth.auth_with_url(url, self.session)

    # --- HenrikDev Delegation ---
    async def get_stats(self, name: str, tag: str, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.session: await self.init_session()
        return await self.henrik.get_stats(name, tag, self.session, region=region)

    async def get_account_info(self, name: str, tag: str) -> Optional[Dict[str, Any]]:
        if not self.session: await self.init_session()
        return await self.henrik.get_account_info(name, tag, self.session)

    async def get_recent_matches(self, name: str, tag: str, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        if not self.session: await self.init_session()
        return await self.henrik.get_recent_matches(name, tag, self.session, region=region)

    # --- Storefront/Riot API ---
    async def get_shop(self) -> Optional[Dict[str, Any]]:
        """Fetch user's daily shop storefront"""
        if not self.puuid or 'X-Riot-Entitlements-JWT' not in self.headers or not self.session:
            return None
        
        url = f"https://pd.{self.region}.a.pvp.net/store/v3/storefront/{self.puuid}"
        try:
            async with self.session.post(url, headers=self.headers, json={}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('SkinsPanelLayout', {})
                else:
                    logger.error(f"Shop API Error {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"Failed to get shop: {e}")
        return None

    async def get_nightmarket(self) -> Optional[Dict[str, Any]]:
        """Fetch user's Night Market (BonusStore)"""
        if not self.puuid or 'X-Riot-Entitlements-JWT' not in self.headers or not self.session:
            return None
        
        url = f"https://pd.{self.region}.a.pvp.net/store/v3/storefront/{self.puuid}"
        try:
            async with self.session.post(url, headers=self.headers, json={}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('BonusStore', {})
                else:
                    logger.error(f"Night Market API Error {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"Failed to get Night Market: {e}")
        return None

    # --- Asset Delegation ---
    async def get_skin_details(self, level_uuid: str) -> Optional[Dict[str, Any]]:
        if not self.session: await self.init_session()
        return await self.assets.get_skin_details(level_uuid, self.session)

    def get_rarity_info(self, rarity_uuid: Optional[str]) -> Dict[str, Any]:
        return self.assets.get_rarity_info(rarity_uuid)

    def get_hardcoded_price(self, rarity_uuid: Optional[str], is_melee: bool = False, level_uuid: Optional[str] = None) -> int:
        return self.assets.get_hardcoded_price(rarity_uuid, is_melee, level_uuid)

    def is_melee_weapon(self, weapon_type: str, skin_name: str) -> bool:
        return self.assets.is_melee_weapon(weapon_type, skin_name)

    # --- User Management ---
    async def link_user(self, discord_id: int, name: str, tag: str) -> None:
        await self.user_manager.link_user(discord_id, name, tag)

    def get_user_link(self, discord_id: int) -> Optional[Tuple[str, str]]:
        return self.user_manager.get_user_link(discord_id)

    async def unlink_user(self, discord_id: int) -> bool:
        return await self.user_manager.unlink_user(discord_id)

    # --- UX Helper ---
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
