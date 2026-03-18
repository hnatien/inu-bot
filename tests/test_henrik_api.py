"""Tests for utils/henrik_api.py — HenrikDev API wrapper."""
import os
import pytest
from unittest.mock import patch

from utils.henrik_api import HenrikAPI
from tests.conftest import FakeSession, FakeResponse


class TestHenrikAPIInit:
    @patch.dict(os.environ, {"HENRIK_API_KEY": "test-key-123", "RIOT_REGION": "eu"})
    def test_loads_config_from_env(self):
        api = HenrikAPI()
        assert api.henrik_key == "test-key-123"
        assert api.region == "eu"

    @patch.dict(os.environ, {"RIOT_REGION": "NA"}, clear=False)
    def test_region_normalized_to_lowercase(self):
        api = HenrikAPI()
        assert api.region == "na"

    @patch.dict(os.environ, {}, clear=True)
    def test_defaults_region_to_ap(self):
        api = HenrikAPI()
        assert api.region == "ap"


class TestRequest:
    @pytest.fixture
    def api(self):
        with patch.dict(os.environ, {"HENRIK_API_KEY": "key123"}):
            return HenrikAPI()

    async def test_successful_request(self, api, fake_session):
        fake_session.add("test-endpoint", FakeResponse(
            json_data={"status": 200, "data": {"rank": "Gold 1"}},
            status=200
        ))
        result = await api._request("test-endpoint", fake_session)
        assert result is not None
        assert result["status"] == 200

    async def test_returns_none_on_404(self, api, fake_session):
        fake_session.add("bad-endpoint", FakeResponse(status=404, json_data={}))
        result = await api._request("bad-endpoint", fake_session)
        assert result is None

    async def test_returns_none_on_401(self, api, fake_session):
        fake_session.add("auth-fail", FakeResponse(status=401, json_data={}))
        result = await api._request("auth-fail", fake_session)
        assert result is None


class TestGetStats:
    @pytest.fixture
    def api(self):
        with patch.dict(os.environ, {"HENRIK_API_KEY": "key", "RIOT_REGION": "ap"}):
            return HenrikAPI()

    async def test_calls_correct_endpoint(self, api, fake_session):
        fake_session.add("v3/mmr/ap/pc/TenZ/SEN", FakeResponse(
            json_data={"status": 200}, status=200
        ))
        result = await api.get_stats("TenZ", "SEN", fake_session)
        assert result is not None

    async def test_custom_region(self, api, fake_session):
        fake_session.add("v3/mmr/eu/pc/Player/TAG", FakeResponse(
            json_data={"status": 200}, status=200
        ))
        result = await api.get_stats("Player", "TAG", fake_session, region="eu")
        assert result is not None

    async def test_url_encodes_special_chars(self, api, fake_session):
        fake_session.add("v3/mmr/ap/pc/Name%20With%20Spaces/TAG", FakeResponse(
            json_data={"status": 200}, status=200
        ))
        result = await api.get_stats("Name With Spaces", "TAG", fake_session)
        assert result is not None


class TestGetAccountInfo:
    async def test_calls_v1_account_endpoint(self, fake_session):
        with patch.dict(os.environ, {"HENRIK_API_KEY": "key"}):
            api = HenrikAPI()
        fake_session.add("v1/account/Foo/Bar", FakeResponse(
            json_data={"status": 200, "data": {"name": "Foo", "tag": "Bar"}},
            status=200
        ))
        result = await api.get_account_info("Foo", "Bar", fake_session)
        assert result is not None
        assert result["data"]["name"] == "Foo"


class TestGetRecentMatches:
    async def test_calls_v3_matches_endpoint(self, fake_session):
        with patch.dict(os.environ, {"HENRIK_API_KEY": "key", "RIOT_REGION": "na"}):
            api = HenrikAPI()
        fake_session.add("v3/matches/na/Foo/Bar", FakeResponse(
            json_data={"status": 200, "data": []},
            status=200
        ))
        result = await api.get_recent_matches("Foo", "Bar", fake_session)
        assert result is not None
