from discord.ext import commands


class CogBase(commands.Cog):
    """Shared base class for all inu-bot cogs."""

    async def _get_lang(self, user_id: int) -> str:
        return await self.api.get_language(user_id)
