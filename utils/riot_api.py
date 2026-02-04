import aiohttp
import os
import re
import json
import base64
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('ValorantAPI')

class ValorantAPI:
    """Wrapper for various Valorant APIs (Riot, HenrikDev, Valorant-API.com)"""
    
    def __init__(self) -> None:
        self.henrik_key: Optional[str] = os.getenv("HENRIK_API_KEY")
        self.region: str = os.getenv("RIOT_REGION", "ap")
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers: Dict[str, str] = {'Content-Type': 'application/json'}
        self.puuid: str = ""
        self.game_name: str = ""
        self.tag_line: str = ""
        
        # In-memory cache
        self.skin_map: Dict[str, Dict[str, Any]] = {}
        self.rarity_map: Dict[str, Dict[str, Any]] = {}
        self.price_overrides: Dict[str, int] = {}
        
        # Constants
        self.VP_IDS = ["85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741", "85ad2bf4-453b-4c30-b744-fbb39b1a53aa"]
        self.VP_ICON_URL = "https://media.valorant-api.com/currencies/85ad13f7-3d1b-5128-9eb2-7cd8ee0b5741/displayicon.png"
        
        # Hardcoded Rarity Data (Defaults, matched to official Riot UUIDs)
        self.RARITY_DATA = {
            '12683d76-48d7-84a3-4e09-6985794f0445': {'name': 'Select', 'color': 0x5a9fe2, 'gun_price': 875, 'melee_price': 1750},
            '0cebb8be-46d7-c12a-d306-e9907bfc5a25': {'name': 'Deluxe', 'color': 0x009587, 'gun_price': 1275, 'melee_price': 2550},
            '60bca009-4182-7998-dee7-b8a2558dc369': {'name': 'Premium', 'color': 0xd1548d, 'gun_price': 1775, 'melee_price': 3550},
            'e046854e-406c-37f4-6607-19a9ba8426fc': {'name': 'Exclusive', 'color': 0xf5955b, 'gun_price': 2175, 'melee_price': 4350},
            '411e4a55-4e59-7757-41f0-86a53f101bb5': {'name': 'Ultra', 'color': 0xfad663, 'gun_price': 2475, 'melee_price': 4950}
        }

    async def init_session(self) -> aiohttp.ClientSession:
        """Initialize ClientSession and prefetch global data"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            await self.load_price_data()
            await self.fetch_all_data()
        return self.session

    async def load_price_data(self) -> None:
        """Load hardcoded price data from JSON file"""
        try:
            import aiofiles
            # Use absolute path for reliability
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "skin_prices.json")
            if not os.path.exists(path):
                logger.warning(f"Price data file not found at {path}")
                return

            async with aiofiles.open(path, mode='r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Update RARITY_DATA
                for tier_uuid, tier_info in data.get('tiers', {}).items():
                    self.RARITY_DATA[tier_uuid] = {
                        'name': tier_info['name'],
                        'color': tier_info['color'],
                        'gun_price': tier_info.get('gun', 0),
                        'melee_price': tier_info.get('melee', 0)
                    }
                
                # Load Overrides
                self.price_overrides = data.get('overrides', {})
                logger.info(f"Loaded {len(self.price_overrides)} price overrides.")
        except Exception as e:
            logger.error(f"Failed to load skin price data: {e}")

    async def fetch_all_data(self) -> None:
        """Prefetch weapon skins and rarity metadata for faster lookups"""
        if not self.session:
            return
            
        try:
            # Prefetch weapon skins
            async with self.session.get("https://valorant-api.com/v1/weapons?language=en-US") as resp:
                data = await resp.json()
                if data.get('status') == 200:
                    for weapon in data.get('data', []):
                        for skin in weapon.get('skins', []):
                            for level in skin.get('levels', []):
                                self.skin_map[level['uuid']] = {
                                    'name': skin['displayName'],
                                    'icon': level.get('displayIcon') or skin.get('displayIcon'),
                                    'rarity': skin.get('contentTierUuid'),
                                    'weapon': weapon['displayName']
                                }
                                
            # Prefetch rarity metadata
            async with self.session.get("https://valorant-api.com/v1/contenttiers") as resp:
                data = await resp.json()
                if data.get('status') == 200:
                    for tier in data.get('data', []):
                        self.rarity_map[tier['uuid']] = {
                            'name': tier['devName'],
                            'icon': tier['displayIcon']
                        }
        except Exception as e:
            logger.error(f"Error prefetching Valorant data: {e}")

    def get_auth_link(self) -> str:
        """Get the Riot OAuth2 authorization link"""
        return (
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in"
            "&client_id=play-valorant-web-prod"
            "&response_type=token%20id_token"
            "&nonce=1"
            "&scope=account%20openid"
        )

    def _get_riot_client_platform(self) -> str:
        """Generate base64 encoded Riot Client Platform header"""
        data = {
            "platformType": "PC",
            "platformOS": "Windows",
            "platformOSVersion": "10.0.19042.1.256.64bit",
            "platformChipset": "Unknown"
        }
        return base64.b64encode(json.dumps(data).encode()).decode()

    async def get_client_version(self) -> str:
        """Get the latest Riot Client version"""
        if not self.session:
            await self.init_session()
        async with self.session.get("https://valorant-api.com/v1/version") as resp: # type: ignore
            data = await resp.json()
            return data['data']['riotClientVersion']

    async def auth_with_url(self, url: str) -> Tuple[bool, str]:
        """Authenticate using the redirect URL from Riot's login"""
        self.headers.update({
            'User-Agent': "ShooterGame/13 Windows/10.0.19043.1.256.64bit",
            'X-Riot-ClientPlatform': self._get_riot_client_platform(),
            'Accept-Language': "en-US,en;q=0.5",
            'referer': "https://github.com/giorgi-o/SkinPeek"
        })
        
        try:
            if not self.session: await self.init_session()
            
            # 1. Update Client Version
            version = await self.get_client_version()
            self.headers['X-Riot-ClientVersion'] = version

            # 2. Extract Access Token
            access_token_match = re.search(r'access_token=([^&]+)', url)
            if not access_token_match:
                return False, "Không tìm thấy Access Token. Hãy copy toàn bộ URL."
            
            access_token = access_token_match.group(1)
            self.headers['Authorization'] = f"Bearer {access_token}"

            # 3. Get Entitlements Token
            async with self.session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=self.headers, json={}) as resp: # type: ignore
                data = await resp.json()
                if resp.status != 200:
                    return False, f"Lỗi Entitlements ({resp.status}): {data.get('message', 'Unknown Error')}"
                self.headers['X-Riot-Entitlements-JWT'] = data['entitlements_token']

            # 4. Get User Info (PUUID)
            async with self.session.get('https://auth.riotgames.com/userinfo', headers=self.headers) as resp: # type: ignore
                data = await resp.json()
                self.puuid = data.get('sub', "")
                acct = data.get('acct', {})
                self.game_name = acct.get('game_name', 'Player')
                self.tag_line = acct.get('tag_line', 'NA1')
                return (True, "Xác thực thành công!") if self.puuid else (False, "Không tìm thấy User ID.")
                
        except Exception as e:
            logger.error(f"Auth error: {e}")
            return False, f"Lỗi hệ thống: {str(e)}"

    async def get_shop(self) -> Optional[Dict[str, Any]]:
        """Fetch user's daily shop storefront"""
        if not self.puuid or 'X-Riot-Entitlements-JWT' not in self.headers or not self.session:
            return None
        
        url = f"https://pd.{self.region}.a.pvp.net/store/v3/storefront/{self.puuid}"
        try:
            async with self.session.post(url, headers=self.headers, json={}) as resp: # type: ignore
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
            async with self.session.post(url, headers=self.headers, json={}) as resp: # type: ignore
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('BonusStore', {})
                else:
                    logger.error(f"Night Market API Error {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"Failed to get Night Market: {e}")
        return None

    async def get_skin_details(self, level_uuid: str) -> Optional[Dict[str, Any]]:
        """Lookup skin details from cache or Valorant-API"""
        if level_uuid in self.skin_map:
            return self.skin_map[level_uuid]
        
        if not self.session: await self.init_session()
        url = f"https://valorant-api.com/v1/weapons/skinlevels/{level_uuid}?language=en-US"
        try:
            async with self.session.get(url) as resp: # type: ignore
                 if resp.status == 200:
                    data = await resp.json()
                    return data.get('data')
        except Exception as e:
            logger.error(f"Failed to get skin details for {level_uuid}: {e}")
        return None

    def get_rarity_info(self, rarity_uuid: Optional[str]) -> Dict[str, Any]:
        """Get color, name and standard price for a rarity"""
        return self.RARITY_DATA.get(rarity_uuid or "", {'name': 'Unknown', 'color': 0x2b2d31, 'gun_price': 0, 'melee_price': 0})

    def get_hardcoded_price(self, rarity_uuid: Optional[str], is_melee: bool = False, level_uuid: Optional[str] = None) -> int:
        """Get the standard price for a skin rarity based on weapon type, checked against overrides"""
        if level_uuid and level_uuid in self.price_overrides:
            return self.price_overrides[level_uuid]
            
        info = self.get_rarity_info(rarity_uuid)
        return info.get('melee_price' if is_melee else 'gun_price', 0)

    async def _henrik_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Generic wrapper for HenrikDev API requests"""
        if not self.session: await self.init_session()
        url = f"https://api.henrikdev.xyz/valorant/{endpoint}"
        h = {"Authorization": self.henrik_key} if self.henrik_key else {}
        try:
            async with self.session.get(url, headers=h) as resp: # type: ignore
                return await resp.json() if resp.status == 200 else None
        except Exception as e:
            logger.error(f"HenrikDev API Error ({endpoint}): {e}")
            return None

    async def get_stats(self, name: str, tag: str) -> Optional[Dict[str, Any]]:
        """Get MMR/Rank stats"""
        return await self._henrik_request(f"v1/mmr/{self.region}/{name}/{tag}")

    async def get_account_info(self, name: str, tag: str) -> Optional[Dict[str, Any]]:
        """Get general account info (level, card)"""
        return await self._henrik_request(f"v1/account/{name}/{tag}")

    async def get_recent_matches(self, name: str, tag: str) -> Optional[Dict[str, Any]]:
        """Get history of recent matches"""
        return await self._henrik_request(f"v3/matches/{self.region}/{name}/{tag}?size=5")

    def get_rank_assets(self, rank_name: str) -> Tuple[int, str]:
        """Get color and icon URL for a specific rank with correct tier handling"""
        rank_name = rank_name.lower()
        color = 0x2b2d31
        # Default Unrated icon
        icon = "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/0/largeicon.png"
        
        # Base indices for each rank (Tier 1)
        ranks = {
            "iron": (0x565656, 3), "bronze": (0x8c7857, 6), "silver": (0xc0c0c0, 9),
            "gold": (0xffd700, 12), "platinum": (0x3e8ca7, 15), "diamond": (0xb48bd6, 18),
            "ascendant": (0x62a67e, 21), "immortal": (0xbf3650, 24), "radiant": (0xffffaa, 27)
        }
        
        for r, (c, base_idx) in ranks.items():
            if r in rank_name:
                color = c
                offset = 0
                if " 2" in rank_name: offset = 1
                elif " 3" in rank_name: offset = 2
                
                # Radiant doesn't have tiers
                if r == "radiant": offset = 0
                
                icon = f"https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/{base_idx + offset}/largeicon.png"
                break
        return color, icon

    async def close(self) -> None:
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
