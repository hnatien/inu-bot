import logging
import os
from typing import Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger('UserManager')

class UserManager:
    """Manages linking of Discord IDs to Valorant Riot IDs using MongoDB."""
    
    def __init__(self) -> None:
        self.uri = os.getenv("MONGO_URI")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.collection = None
        
    async def load(self) -> None:
        """Initialize MongoDB connection."""
        if not self.uri:
            logger.error("MONGO_URI not found in environment variables.")
            return

        try:
            self.client = AsyncIOMotorClient(self.uri)
            self.db = self.client.get_database("inu_bot")
            self.collection = self.db.users
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")

    async def link_user(self, discord_id: int, name: str, tag: str) -> bool:
        """Link a Discord ID to a Riot ID in MongoDB."""
        if self.collection is None:
            return False

        await self.collection.update_one(
            {"discord_id": str(discord_id)},
            {"$set": {"name": name, "tag": tag}},
            upsert=True
        )
        return True

    async def get_user_link(self, discord_id: int) -> Optional[Tuple[str, str]]:
        """Get the Riot ID and Tag for a Discord ID from MongoDB."""
        if self.collection is None:
            return None

        data = await self.collection.find_one({"discord_id": str(discord_id)})
        if data:
            return data["name"], data["tag"]
        return None

    async def unlink_user(self, discord_id: int) -> bool:
        """Unlink a Discord ID from MongoDB."""
        if self.collection is None:
            return False

        result = await self.collection.delete_one({"discord_id": str(discord_id)})
        return result.deleted_count > 0
