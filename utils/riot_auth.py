import base64
import json
import logging
import re
from typing import Dict, Tuple, Optional

import aiohttp

logger = logging.getLogger('RiotAuth')


class RiotAuth:
    """Handles Riot Games OAuth2 authentication and token management."""

    def __init__(self) -> None:
        self.headers: Dict[str, str] = {
            'Content-Type': 'application/json',
            'User-Agent': "ShooterGame/13 Windows/10.0.19043.1.256.64bit",
            'Accept-Language': "en-US,en;q=0.5",
            'referer': "https://github.com/giorgi-o/SkinPeek"
        }
        self.puuid: str = ""
        self.game_name: str = ""
        self.tag_line: str = ""

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

    async def get_client_version(self, session: aiohttp.ClientSession) -> str:
        """Get the latest Riot Client version from valorant-api.com"""
        async with session.get("https://valorant-api.com/v1/version") as resp:
            data = await resp.json()
            return data['data']['riotClientVersion']

    async def auth_with_url(self, url: str, session: aiohttp.ClientSession) -> Tuple[bool, str]:
        """Authenticate using the redirect URL from Riot's login"""
        self.headers['X-Riot-ClientPlatform'] = self._get_riot_client_platform()
        
        try:
            # 1. Update Client Version
            version = await self.get_client_version(session)
            self.headers['X-Riot-ClientVersion'] = version

            # 2. Extract Access Token
            access_token_match = re.search(r'access_token=([^&]+)', url)
            if not access_token_match:
                return False, "Không tìm thấy Access Token. Hãy copy toàn bộ URL."
            
            access_token = access_token_match.group(1)
            self.headers['Authorization'] = f"Bearer {access_token}"

            # 3. Get Entitlements Token
            async with session.post(
                'https://entitlements.auth.riotgames.com/api/token/v1', 
                headers=self.headers, 
                json={}
            ) as resp:
                data = await resp.json()
                if resp.status != 200:
                    return False, f"Lỗi Entitlements ({resp.status}): {data.get('message', 'Unknown Error')}"
                self.headers['X-Riot-Entitlements-JWT'] = data['entitlements_token']

            # 4. Get User Info (PUUID)
            async with session.get(
                'https://auth.riotgames.com/userinfo', 
                headers=self.headers
            ) as resp:
                data = await resp.json()
                self.puuid = data.get('sub', "")
                acct = data.get('acct', {})
                self.game_name = acct.get('game_name', 'Player')
                self.tag_line = acct.get('tag_line', 'NA1')
                return (True, "Xác thực thành công!") if self.puuid else (False, "Không tìm thấy User ID.")
                
        except Exception as e:
            error_msg = str(e)
            if 'access_token' in error_msg.lower() or 'bearer' in error_msg.lower():
                error_msg = "Authentication failed (details preserved for log)"
            logger.error(f"Auth error: {error_msg}")
            return False, "Lỗi hệ thống khi xác thực. Vui lòng thử lại."
