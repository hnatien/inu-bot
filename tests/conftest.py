"""Shared fixtures for inu-bot tests."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

import pytest

from utils.riot_auth import AuthResult
from utils.constants import RARITY_DATA


# ── Fake HTTP helpers ──────────────────────────────────────────────

class FakeResponse:
    """Simulates an aiohttp response object."""

    def __init__(self, json_data: Any = None, status: int = 200, text: str = ""):
        self._json = json_data
        self.status = status
        self._text = text

    async def json(self):
        return self._json

    async def text(self):
        return self._text

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeSession:
    """Minimal aiohttp.ClientSession stub for unit tests."""

    def __init__(self):
        self.responses: Dict[str, FakeResponse] = {}
        self._default_response = FakeResponse(json_data={}, status=404)

    def add(self, url_fragment: str, response: FakeResponse):
        self.responses[url_fragment] = response

    def _match(self, url: str) -> FakeResponse:
        for fragment, resp in self.responses.items():
            if fragment in url:
                return resp
        return self._default_response

    def get(self, url: str, **kwargs):
        return self._match(url)

    def post(self, url: str, **kwargs):
        return self._match(url)

    async def close(self):
        pass


# ── Fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def fake_session():
    return FakeSession()


@pytest.fixture
def sample_auth() -> AuthResult:
    return AuthResult(
        puuid="test-puuid-1234",
        game_name="TestPlayer",
        tag_line="1234",
        headers={
            "Authorization": "Bearer fake-token",
            "X-Riot-Entitlements-JWT": "fake-jwt",
            "Content-Type": "application/json",
        },
    )


@pytest.fixture
def sample_account_data() -> Dict[str, Any]:
    return {
        "status": 200,
        "data": {
            "name": "TestPlayer",
            "tag": "1234",
            "account_level": 150,
            "region": "ap",
            "card": {
                "small": "https://example.com/card_small.png",
                "large": "https://example.com/card_large.png",
            },
        },
    }


@pytest.fixture
def sample_mmr_data() -> Dict[str, Any]:
    return {
        "status": 200,
        "data": {
            "current": {
                "tier": {"name": "Diamond 2"},
                "rr": 67,
            },
            "peak": {
                "tier": {"name": "Immortal 1"},
            },
        },
    }


@pytest.fixture
def sample_matches_data() -> Dict[str, Any]:
    return {
        "status": 200,
        "data": [
            {
                "metadata": {
                    "mode": "Competitive",
                    "map": "Ascent",
                    "rounds_played": 24,
                },
                "players": {
                    "all_players": [
                        {
                            "name": "TestPlayer",
                            "tag": "1234",
                            "team": "blue",
                            "character": "Jett",
                            "stats": {
                                "kills": 25,
                                "deaths": 15,
                                "assists": 5,
                                "score": 6000,
                                "headshots": 12,
                                "bodyshots": 30,
                                "legshots": 3,
                            },
                        }
                    ]
                },
                "teams": {
                    "blue": {"has_won": True},
                    "red": {"has_won": False},
                },
            }
        ],
    }
