import asyncio
import json
import os
import aiofiles
from typing import Dict, Optional, Tuple

class UserManager:
    """Manages linking of Discord IDs to Valorant Riot IDs."""
    
    def __init__(self, file_path: str = "assets/users.json") -> None:
        self.file_path = file_path
        self.users: Dict[str, Dict[str, str]] = {}
        self._lock = asyncio.Lock()
        
    async def load(self) -> None:
        """Load linked accounts from JSON file."""
        if not os.path.exists(self.file_path):
            # Ensure assets directory exists
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            async with aiofiles.open(self.file_path, mode='w') as f:
                await f.write(json.dumps({}))
            return

        async with aiofiles.open(self.file_path, mode='r') as f:
            content = await f.read()
            try:
                self.users = json.loads(content)
            except json.JSONDecodeError:
                self.users = {}

    async def save(self) -> None:
        """Save current linked accounts to JSON file."""
        async with self._lock:
            async with aiofiles.open(self.file_path, mode='w') as f:
                await f.write(json.dumps(self.users, indent=2))

    async def link_user(self, discord_id: int, name: str, tag: str) -> None:
        """Link a Discord ID to a Riot ID."""
        self.users[str(discord_id)] = {"name": name, "tag": tag}
        await self.save()

    def get_user_link(self, discord_id: int) -> Optional[Tuple[str, str]]:
        """Get the Riot ID and Tag for a Discord ID."""
        data = self.users.get(str(discord_id))
        if data:
            return data["name"], data["tag"]
        return None

    async def unlink_user(self, discord_id: int) -> bool:
        """Unlink a Discord ID."""
        if str(discord_id) in self.users:
            del self.users[str(discord_id)]
            await self.save()
            return True
        return False
