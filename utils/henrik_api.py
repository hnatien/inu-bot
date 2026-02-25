import logging
import os
import urllib.parse
from typing import Dict, Optional, Any

import aiohttp

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
logger = logging.getLogger('HenrikAPI')


class HenrikAPI:
    """Wrapper for HenrikDev Valorant API (MMR, Account, Matches)."""

    def __init__(self) -> None:
        self.henrik_key: Optional[str] = os.getenv("HENRIK_API_KEY")
        if self.henrik_key:
            self.henrik_key = self.henrik_key.strip()
            
        region_env = os.getenv("RIOT_REGION", "ap")
        self.region: str = region_env.strip().lower()
        
        if not self.henrik_key:
            logger.error("HENRIK_API_KEY NOT FOUND IN ENVIRONMENT VARIABLES")

    async def _request(self, endpoint: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Generic wrapper for HenrikDev API requests"""
        url = f"https://api.henrikdev.xyz/valorant/{endpoint}"
        
        h = {"Authorization": self.henrik_key} if self.henrik_key else {}
        try:
            async with session.get(url, headers=h) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.warning(f"HenrikDev API Error ({endpoint}): Status {resp.status}")
                    # Log more detail for 401
                    if resp.status == 401:
                        logger.error(f"AUTHENTICATION FAILED: Check if HENRIK_API_KEY is valid. Key length: {len(self.henrik_key) if self.henrik_key else 0}")
                    return None
        except Exception as e:
            logger.error(f"HenrikDev API Exception ({endpoint}): {e}")
            return None

    async def get_stats(self, name: str, tag: str, session: aiohttp.ClientSession, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get MMR/Rank stats (v3 is the latest)"""
        safe_name = urllib.parse.quote(name)
        safe_tag = urllib.parse.quote(tag)
        target_region = region if region else self.region
        # Using pc as default platform for mmr v3
        return await self._request(f"v3/mmr/{target_region}/pc/{safe_name}/{safe_tag}", session)

    async def get_account_info(self, name: str, tag: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        """Get general account info (v1)"""
        import urllib.parse
        safe_name = urllib.parse.quote(name)
        safe_tag = urllib.parse.quote(tag)
        return await self._request(f"v1/account/{safe_name}/{safe_tag}", session)

    async def get_recent_matches(self, name: str, tag: str, session: aiohttp.ClientSession, region: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get history of recent matches (v3)"""
        import urllib.parse
        safe_name = urllib.parse.quote(name)
        safe_tag = urllib.parse.quote(tag)
        target_region = region if region else self.region
        return await self._request(f"v3/matches/{target_region}/{safe_name}/{safe_tag}?size=5", session)
