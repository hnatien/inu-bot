import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, Optional

from utils import ValorantAPI
from utils.i18n import t
from views.stat_views import StatView, process_and_send_stats
from cogs import CogBase

class StatsCog(CogBase):
    """Cog for Valorant player statistics and account linking."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = bot.v_api

    @app_commands.command(name="link", description="Link your Discord account to a Valorant Riot ID")
    @app_commands.describe(name="Riot ID (e.g. TenZ)", tag="Tagline without # (e.g. SEN)")
    async def link(self, interaction: discord.Interaction, name: str, tag: str) -> None:
        """Links the user's Discord ID to a Riot ID."""
        lang = await self._get_lang(interaction.user.id)
        if not (1 <= len(name) <= 16) or not (3 <= len(tag) <= 5):
            await interaction.response.send_message(f"[Error] {t('link_invalid_id', lang)}", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)

        acc_data = await self.api.get_account_info(name, tag)
        if not acc_data or acc_data.get('status') != 200:
            await interaction.followup.send(f"[Error] {t('link_not_found', lang, name=name, tag=tag)}", ephemeral=True)
            return
            
        real_name = acc_data['data']['name']
        real_tag = acc_data['data']['tag']
        real_region = str(acc_data['data'].get('region', 'ap')).lower()
        
        success = await self.api.link_user(interaction.user.id, real_name, real_tag, real_region)
        if success:
            await interaction.followup.send(f"[Success] {t('link_success', lang, name=real_name, tag=real_tag)}", ephemeral=True)
        else:
            await interaction.followup.send(f"[Error] {t('link_db_error', lang)}", ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink your Valorant account from Discord")
    async def unlink(self, interaction: discord.Interaction) -> None:
        """Unlinks the user's Discord ID."""
        lang = await self._get_lang(interaction.user.id)
        success = await self.api.unlink_user(interaction.user.id)
        if success:
            await interaction.response.send_message(f"[Success] {t('unlink_success', lang)}", ephemeral=True)
        else:
            await interaction.response.send_message(f"[Error] {t('unlink_error', lang)}", ephemeral=True)

    @app_commands.command(name="stat", description="Lookup Valorant player statistics globally")
    @app_commands.describe(user="The Discord user to check", name="Riot ID (manual)", tag="Tagline (manual)")
    async def stat_slash(
        self, 
        interaction: discord.Interaction, 
        user: Optional[discord.Member] = None,
        name: Optional[str] = None,
        tag: Optional[str] = None
    ) -> None:
        """Lookup stats with automatic linked account detection."""
        lang = await self._get_lang(interaction.user.id)
        
        if name and tag:
            if not (1 <= len(name) <= 16) or not (3 <= len(tag) <= 5):
                await interaction.response.send_message(f"[Error] {t('link_invalid_id', lang)}", ephemeral=True)
                return
            await interaction.response.defer()
            await process_and_send_stats(interaction, self.api, name, tag, lang=lang)
            return
            
        target = user or interaction.user
        link = await self.api.get_user_link(target.id)
        
        if link:
            await interaction.response.defer()
            await process_and_send_stats(interaction, self.api, link[0], link[1], region=link[2], lang=lang)
        elif user:
            await interaction.response.send_message(f"[Error] {t('user_not_linked', lang, name=user.display_name)}", ephemeral=True)
        else:
            await self._send_stat_intro(interaction, lang=lang)

    @commands.command(name="stat")
    async def stat_prefix(self, ctx: commands.Context) -> None:
        """Prefix command version with automatic lookup."""
        lang = await self._get_lang(ctx.author.id)
        link = await self.api.get_user_link(ctx.author.id)
        if link:
            await process_and_send_stats(ctx, self.api, link[0], link[1], region=link[2], lang=lang)
        else:
            await self._send_stat_intro(ctx, lang=lang)

    async def _send_stat_intro(self, context: Union[discord.Interaction, commands.Context], lang: str = "en") -> None:
        """Sends the initial interaction for stat lookup."""
        user_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id
        view = StatView(self.api, user_id, lang=lang)
        embed = discord.Embed(
            title=t("title_valorant_tracker", lang),
            description=t("stat_intro", lang),
            color=0xFD4553
        )
        embed.set_thumbnail(url="https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/24/largeicon.png")
        embed.set_footer(text=t("footer", lang))

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view)
            try:
                view.message = await context.original_response()
            except discord.HTTPException:
                pass
        else:
            view.message = await context.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
