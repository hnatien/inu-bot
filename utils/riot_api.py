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
        self.all_offers: List[Dict[str, Any]] = []

    async def init_session(self) -> aiohttp.ClientSession:
        """Initialize ClientSession and prefetch global data"""
        if not self.session:
            self.session = aiohttp.ClientSession()
            await self.fetch_all_data()
        return self.session

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
        json_str = json.dumps(data, indent='\t', separators=(',', ': ')).replace('\n', '\r\n')
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

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

    async def get_all_offers(self) -> List[Dict[str, Any]]:
        """Fetch global store offers (prices)"""
        if self.all_offers: return self.all_offers
        if not self.session: await self.init_session()
        
        url = f"https://pd.{self.region}.a.pvp.net/store/v1/offers/"
        try:
            async with self.session.get(url, headers=self.headers) as resp: # type: ignore
                if resp.status == 200:
                    data = await resp.json()
                    self.all_offers = data.get('Offers', [])
                    return self.all_offers
        except Exception as e:
            logger.warning(f"Failed to fetch global offers: {e}")
        return []

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

    def get_rarity_color(self, rarity_uuid: Optional[str]) -> int:
        """Get Discord embed color based on skin rarity"""
        color_map = {
            '0cebb8be-46d7-c12a-d306-e9907bfc5a25': 0x009984, # Select
            'e046854e-406c-37f4-6607-19a9ba8426fc': 0xf99358, # Deluxe
            '60bca009-4182-7998-dee7-b8a2558dc369': 0xd1538c, # Premium
            '12683d76-48d7-84a3-4e09-6985794f0445': 0x5a9fe1, # Ultra
            '411e4a55-4e59-7757-41f0-86a53f101bb5': 0xf9d563  # Exclusive
        }
        return color_map.get(rarity_uuid or "", 0x2b2d31)

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
        return await self._henrik_request(f"v3/matches/{self.region}/{name}/{tag}?size=3")

    def get_rank_assets(self, rank_name: str) -> Tuple[int, str]:
        """Get color and icon URL for a specific rank"""
        rank_name = rank_name.lower()
        color = 0x2b2d31
        icon = "https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/0/largeicon.png"
        
        ranks = {
            "iron": (0x565656, 3), "bronze": (0x8c7857, 6), "silver": (0xc0c0c0, 9),
            "gold": (0xffd700, 12), "platinum": (0x3e8ca7, 15), "diamond": (0xb48bd6, 18),
            "ascendant": (0x62a67e, 21), "immortal": (0xbf3650, 24), "radiant": (0xffffaa, 25)
        }
        
        for r, (c, idx) in ranks.items():
            if r in rank_name:
                color, icon = c, f"https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/{idx}/largeicon.png"
                break
        return color, icon

    async def close(self) -> None:
        """Close the aiohttp session"""
        if self.session:
            await self.session.close()
