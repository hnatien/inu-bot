import base64
import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, Tuple, Optional

import aiohttp

logger = logging.getLogger('RiotAuth')


@dataclass
class AuthResult:
    """Per-request authentication context returned from auth_with_url."""
    puuid: str
    game_name: str
    tag_line: str
    headers: Dict[str, str]


class RiotAuth:
    """Handles Riot Games OAuth2 authentication and token management."""

    BASE_HEADERS: Dict[str, str] = {
        'Content-Type': 'application/json',
        'User-Agent': "ShooterGame/13 Windows/10.0.19043.1.256.64bit",
        'Accept-Language': "en-US,en;q=0.5",
        'referer': "https://github.com/giorgi-o/SkinPeek"
    }

    @staticmethod
    def get_auth_link() -> str:
        return (
            "https://auth.riotgames.com/authorize?redirect_uri=https%3A%2F%2Fplayvalorant.com%2Fopt_in"
            "&client_id=play-valorant-web-prod"
            "&response_type=token%20id_token"
            "&nonce=1"
            "&scope=account%20openid"
        )

    @staticmethod
    def _get_riot_client_platform() -> str:
        data = {
            "platformType": "PC",
            "platformOS": "Windows",
            "platformOSVersion": "10.0.19042.1.256.64bit",
            "platformChipset": "Unknown"
        }
        return base64.b64encode(json.dumps(data).encode()).decode()

    @staticmethod
    async def _get_client_version(session: aiohttp.ClientSession) -> str:
        async with session.get("https://valorant-api.com/v1/version") as resp:
            data = await resp.json()
            return data['data']['riotClientVersion']

    async def auth_with_url(self, url: str, session: aiohttp.ClientSession) -> Tuple[bool, str, Optional[AuthResult]]:
        """Authenticate using the redirect URL. Returns per-request AuthResult to avoid race conditions."""
        headers = dict(self.BASE_HEADERS)
        headers['X-Riot-ClientPlatform'] = self._get_riot_client_platform()

        try:
            version = await self._get_client_version(session)
            headers['X-Riot-ClientVersion'] = version

            access_token_match = re.search(r'access_token=([^&]+)', url)
            if not access_token_match:
                return False, "Không tìm thấy Access Token. Hãy copy toàn bộ URL.", None

            access_token = access_token_match.group(1)
            headers['Authorization'] = f"Bearer {access_token}"

            async with session.post(
                'https://entitlements.auth.riotgames.com/api/token/v1',
                headers=headers,
                json={}
            ) as resp:
                data = await resp.json()
                if resp.status != 200:
                    return False, f"Lỗi Entitlements ({resp.status}): {data.get('message', 'Unknown Error')}", None
                headers['X-Riot-Entitlements-JWT'] = data['entitlements_token']

            async with session.get(
                'https://auth.riotgames.com/userinfo',
                headers=headers
            ) as resp:
                data = await resp.json()
                puuid = data.get('sub', "")
                acct = data.get('acct', {})
                game_name = acct.get('game_name', 'Player')
                tag_line = acct.get('tag_line', 'NA1')

                if puuid:
                    return True, "Xác thực thành công!", AuthResult(
                        puuid=puuid, game_name=game_name,
                        tag_line=tag_line, headers=headers
                    )
                return False, "Không tìm thấy User ID.", None

        except Exception as e:
            error_msg = str(e)
            if 'access_token' in error_msg.lower() or 'bearer' in error_msg.lower():
                error_msg = "Authentication failed (details preserved for log)"
            logger.error(f"Auth error: {error_msg}")
            return False, "Lỗi hệ thống khi xác thực. Vui lòng thử lại.", None
