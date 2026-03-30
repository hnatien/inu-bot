import logging
import os
import json
import asyncio
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

from utils.i18n import DEFAULT_LANG
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger('UserManager')

class UserManager:
    """Manages linking of Discord IDs to Valorant Riot IDs using MongoDB or JSON fallback."""
    
    def __init__(self) -> None:
        self.uri = os.getenv("MONGO_URI")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.collection = None
        self.use_mongodb = False
        self.json_file = Path("assets/users.json")
        self.json_data: Dict[str, Any] = {}
        self._json_lock = asyncio.Lock()
        
    async def load(self) -> None:
        """Initialize MongoDB connection, or fallback to JSON file."""
        if not self.uri:
            logger.warning("MONGO_URI not found. Falling back to JSON file storage.")
            await self._load_json_fallback()
            return

        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client.get_database("inu_bot")
            self.collection = self.db.users
            await self.collection.create_index("discord_id", unique=True)
            self.use_mongodb = True
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}. Falling back to JSON file storage.")
            await self._load_json_fallback()

    def _is_mongodb_ready(self) -> bool:
        """Check if MongoDB is properly initialized and ready to use."""
        return self.use_mongodb and self.collection is not None

    async def _find_user_data(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """Fetch user data from MongoDB when available, otherwise from JSON fallback."""
        if self._is_mongodb_ready():
            return await self.collection.find_one({"discord_id": discord_id})
        return self.json_data.get(discord_id)

    async def _load_json_fallback(self) -> None:
        """Load user data from JSON file."""
        if self.json_file.exists():
            try:
                with self.json_file.open("r", encoding="utf-8") as f:
                    self.json_data = json.load(f)
                logger.info(f"Loaded {len(self.json_data)} users from JSON file.")
            except Exception as e:
                logger.error(f"Failed to load JSON file: {e}")
                self.json_data = {}
        else:
            self.json_data = {}
            logger.info("JSON file not found. Starting with empty user data.")

    async def _save_json_fallback(self) -> None:
        """Save user data to JSON file."""
        async with self._json_lock:
            try:
                self.json_file.parent.mkdir(parents=True, exist_ok=True)
                with self.json_file.open("w", encoding="utf-8") as f:
                    json.dump(self.json_data, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to save JSON file: {e}")

    async def link_user(self, discord_id: int, name: str, tag: str, region: str) -> bool:
        """Link a Discord ID to a Riot ID in MongoDB or JSON."""
        discord_id_str = str(discord_id)
        
        if self._is_mongodb_ready():
            result = await self.collection.update_one(
                {"discord_id": discord_id_str},
                {"$set": {"name": name, "tag": tag, "region": region}},
                upsert=True
            )
            return result.acknowledged
        
        # Preserve existing language preference when updating user link
        existing_lang = self.json_data.get(discord_id_str, {}).get("lang", DEFAULT_LANG)
        self.json_data[discord_id_str] = {
            "name": name,
            "tag": tag,
            "region": region,
            "lang": existing_lang
        }
        await self._save_json_fallback()
        return True

    async def get_user_link(self, discord_id: int) -> Optional[Tuple[str, str, Optional[str]]]:
        """Get the Riot ID, Tag, and Region for a Discord ID."""
        discord_id_str = str(discord_id)
        data = await self._find_user_data(discord_id_str)
        
        if data and "name" in data:
            return data["name"], data["tag"], data.get("region")
        return None

    async def unlink_user(self, discord_id: int) -> bool:
        """Unlink a Discord ID."""
        discord_id_str = str(discord_id)
        
        if self._is_mongodb_ready():
            result = await self.collection.delete_one({"discord_id": discord_id_str})
            return result.deleted_count > 0
        
        if discord_id_str in self.json_data:
            del self.json_data[discord_id_str]
            await self._save_json_fallback()
            return True
        return False

    async def get_language(self, discord_id: int) -> str:
        """Get the user's preferred language, or DEFAULT_LANG if not set."""
        discord_id_str = str(discord_id)
        data = await self._find_user_data(discord_id_str)
        
        return data.get("lang", DEFAULT_LANG) if data else DEFAULT_LANG

    async def set_language(self, discord_id: int, lang: str) -> bool:
        """Set the user's preferred language."""
        discord_id_str = str(discord_id)
        
        if self._is_mongodb_ready():
            result = await self.collection.update_one(
                {"discord_id": discord_id_str},
                {"$set": {"lang": lang}},
                upsert=True
            )
            return result.acknowledged
        
        if discord_id_str not in self.json_data:
            self.json_data[discord_id_str] = {}
        self.json_data[discord_id_str]["lang"] = lang
        await self._save_json_fallback()
        return True

    async def close(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
