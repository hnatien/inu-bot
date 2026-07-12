"""Tests for utils/user_manager.py — MongoDB user operations (mocked)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from utils.user_manager import UserManager


@pytest.fixture
def manager():
    """UserManager with mocked MongoDB collection."""
    mgr = UserManager()
    mgr.collection = AsyncMock()
    mgr.use_mongodb = True
    mock_result = MagicMock()
    mock_result.acknowledged = True
    mgr.collection.update_one.return_value = mock_result
    return mgr


class TestLinkUser:
    async def test_link_user_calls_upsert(self, manager):
        result = await manager.link_user(12345, "TenZ", "SEN", "na")
        assert result is True
        manager.collection.update_one.assert_awaited_once()
        call_args = manager.collection.update_one.call_args
        assert call_args[0][0] == {"discord_id": "12345"}
        assert call_args[0][1] == {"$set": {"name": "TenZ", "tag": "SEN", "region": "na"}}
        assert call_args[1]["upsert"] is True

    async def test_link_user_no_collection_falls_back_to_json(self):
        """Test that link_user falls back to JSON when no collection."""
        mgr = UserManager()
        mgr.collection = None
        mgr.use_mongodb = False
        result = await mgr.link_user(12345, "TenZ", "SEN", "na")
        assert result is True
        assert mgr.json_data["12345"]["name"] == "TenZ"


class TestGetUserLink:
    async def test_found_link(self, manager):
        manager.collection.find_one = AsyncMock(return_value={
            "discord_id": "12345",
            "name": "TenZ",
            "tag": "SEN",
            "region": "na",
        })
        result = await manager.get_user_link(12345)
        assert result == ("TenZ", "SEN", "na")

    async def test_not_found(self, manager):
        manager.collection.find_one = AsyncMock(return_value=None)
        result = await manager.get_user_link(99999)
        assert result is None

    async def test_no_name_field(self, manager):
        manager.collection.find_one = AsyncMock(return_value={"discord_id": "12345"})
        result = await manager.get_user_link(12345)
        assert result is None

    async def test_no_collection(self):
        mgr = UserManager()
        mgr.collection = None
        mgr.use_mongodb = False
        result = await mgr.get_user_link(12345)
        assert result is None


class TestUnlinkUser:
    async def test_successful_unlink(self, manager):
        manager.collection.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=1)
        )
        result = await manager.unlink_user(12345)
        assert result is True

    async def test_unlink_not_found(self, manager):
        manager.collection.delete_one = AsyncMock(
            return_value=MagicMock(deleted_count=0)
        )
        result = await manager.unlink_user(99999)
        assert result is False

    async def test_unlink_no_collection(self):
        mgr = UserManager()
        mgr.collection = None
        mgr.use_mongodb = False
        result = await mgr.unlink_user(12345)
        assert result is False


class TestLanguage:
    async def test_get_language_default(self, manager):
        manager.collection.find_one = AsyncMock(return_value=None)
        result = await manager.get_language(12345)
        assert result == "vi"

    async def test_get_language_set(self, manager):
        manager.collection.find_one = AsyncMock(return_value={"lang": "vi"})
        result = await manager.get_language(12345)
        assert result == "vi"

    async def test_get_language_no_lang_field(self, manager):
        manager.collection.find_one = AsyncMock(return_value={"discord_id": "12345"})
        result = await manager.get_language(12345)
        assert result == "vi"

    async def test_set_language(self, manager):
        result = await manager.set_language(12345, "vi")
        assert result is True
        manager.collection.update_one.assert_awaited_once()

    async def test_get_language_no_collection(self):
        mgr = UserManager()
        mgr.collection = None
        mgr.use_mongodb = False
        result = await mgr.get_language(12345)
        assert result == "vi"

    async def test_set_language_no_collection(self):
        """Test that set_language falls back to JSON when no collection."""
        mgr = UserManager()
        mgr.collection = None
        mgr.use_mongodb = False
        result = await mgr.set_language(12345, "vi")
        assert result is True
        assert mgr.json_data["12345"]["lang"] == "vi"


class TestClose:
    async def test_close_with_client(self):
        mgr = UserManager()
        mock_client = MagicMock()
        mgr.client = mock_client
        await mgr.close()
        mock_client.close.assert_called_once()
        assert mgr.client is None

    async def test_close_without_client(self):
        mgr = UserManager()
        mgr.client = None
        await mgr.close()  # Should not raise
