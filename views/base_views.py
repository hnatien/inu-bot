from typing import Optional

import discord

from utils.i18n import t, DEFAULT_LANG


class BaseView(discord.ui.View):
    """Shared base view with automatic on_timeout button disabling."""

    def __init__(self, *args, lang: str = DEFAULT_LANG, **kwargs):
        super().__init__(*args, **kwargs)
        self.message: Optional[discord.Message] = None
        self.lang = lang

    async def on_timeout(self) -> None:
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
                await self.message.reply(
                    t("timeout_expired", self.lang),
                    mention_author=False,
                )
            except (discord.NotFound, discord.HTTPException):
                pass
