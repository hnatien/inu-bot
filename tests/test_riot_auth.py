"""Tests for utils/riot_auth.py — OAuth2 authentication."""
import pytest
from unittest.mock import AsyncMock, patch

from utils.riot_auth import RiotAuth, AuthResult
from tests.conftest import FakeSession, FakeResponse


class TestAuthResult:
    def test_dataclass_fields(self, sample_auth):
        assert sample_auth.puuid == "test-puuid-1234"
        assert sample_auth.game_name == "TestPlayer"
        assert sample_auth.tag_line == "1234"
        assert "Authorization" in sample_auth.headers


class TestGetAuthLink:
    def test_returns_riot_oauth_url(self):
        url = RiotAuth.get_auth_link()
        assert "auth.riotgames.com/authorize" in url
        assert "redirect_uri" in url
        assert "client_id=play-valorant-web-prod" in url
        assert "response_type=token" in url


class TestClientVersionCache:
    async def test_fetches_version(self):
        auth = RiotAuth()
        session = FakeSession()
        session.add("valorant-api.com/v1/version", FakeResponse(
            json_data={"data": {"riotClientVersion": "release-09.00-shipping-15-1234567"}}
        ))
        version = await auth._get_client_version(session)
        assert "release-" in version

    async def test_caches_version(self):
        auth = RiotAuth()
        session = FakeSession()
        session.add("valorant-api.com/v1/version", FakeResponse(
            json_data={"data": {"riotClientVersion": "v1.0"}}
        ))
        v1 = await auth._get_client_version(session)
        # Change response — should still return cached
        session.add("valorant-api.com/v1/version", FakeResponse(
            json_data={"data": {"riotClientVersion": "v2.0"}}
        ))
        v2 = await auth._get_client_version(session)
        assert v1 == v2 == "v1.0"


class TestAuthWithUrl:
    @pytest.fixture
    def auth(self):
        return RiotAuth()

    @pytest.fixture
    def session_with_version(self, fake_session):
        fake_session.add("valorant-api.com/v1/version", FakeResponse(
            json_data={"data": {"riotClientVersion": "release-09.00"}}
        ))
        return fake_session

    async def test_rejects_invalid_url_domain(self, auth, session_with_version):
        ok, msg, result = await auth.auth_with_url(
            "https://evil-site.com/opt_in#access_token=abc123",
            session_with_version
        )
        assert ok is False
        assert result is None

    async def test_rejects_missing_token(self, auth, session_with_version):
        ok, msg, result = await auth.auth_with_url(
            "https://playvalorant.com/opt_in#no_token_here",
            session_with_version
        )
        assert ok is False
        assert result is None

    async def test_successful_auth_flow(self, auth, session_with_version):
        session = session_with_version
        session.add("entitlements.auth.riotgames.com", FakeResponse(
            json_data={"entitlements_token": "fake-jwt-token"}
        ))
        session.add("auth.riotgames.com/userinfo", FakeResponse(
            json_data={
                "sub": "puuid-abc-123",
                "acct": {"game_name": "Player1", "tag_line": "NA1"},
            }
        ))
        ok, msg, result = await auth.auth_with_url(
            "https://playvalorant.com/opt_in#access_token=valid_token_here&scope=openid",
            session
        )
        assert ok is True
        assert isinstance(result, AuthResult)
        assert result.puuid == "puuid-abc-123"
        assert result.game_name == "Player1"
        assert result.tag_line == "NA1"

    async def test_entitlements_failure(self, auth, session_with_version):
        session = session_with_version
        session.add("entitlements.auth.riotgames.com", FakeResponse(
            json_data={"message": "Unauthorized"}, status=401
        ))
        ok, msg, result = await auth.auth_with_url(
            "https://playvalorant.com/opt_in#access_token=bad_token",
            session
        )
        assert ok is False
        assert result is None

    async def test_no_puuid_returns_failure(self, auth, session_with_version):
        session = session_with_version
        session.add("entitlements.auth.riotgames.com", FakeResponse(
            json_data={"entitlements_token": "jwt"}
        ))
        session.add("auth.riotgames.com/userinfo", FakeResponse(
            json_data={"sub": "", "acct": {}}
        ))
        ok, msg, result = await auth.auth_with_url(
            "https://playvalorant.com/opt_in#access_token=token123",
            session
        )
        assert ok is False
        assert result is None
