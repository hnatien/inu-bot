import discord
from discord.ext import commands
from discord import app_commands
from typing import Union, Optional

from utils import ValorantAPI
from views.stat_views import StatView, process_and_send_stats

class StatsCog(commands.Cog):
    """Cog for Valorant player statistics and account linking."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = getattr(bot, 'v_api')

    @app_commands.command(name="link", description="Link your Discord account to a Valorant Riot ID")
    @app_commands.describe(name="Riot ID (e.g. TenZ)", tag="Tagline without # (e.g. SEN)")
    async def link(self, interaction: discord.Interaction, name: str, tag: str) -> None:
        """Links the user's Discord ID to a Riot ID."""
        await interaction.response.defer(ephemeral=True)
        
        acc_data = await self.api.get_account_info(name, tag)
        if not acc_data or acc_data.get('status') != 200:
            await interaction.followup.send(f"[Error] Could not find account **{name}#{tag}**. Please check again.", ephemeral=True)
            return
            
        real_name = acc_data['data']['name']
        real_tag = acc_data['data']['tag']
        real_region = str(acc_data['data'].get('region', 'ap')).lower()
        
        success = await self.api.link_user(interaction.user.id, real_name, real_tag, real_region)
        if success:
            await interaction.followup.send(f"[Success] Successfully linked your account to **{real_name}#{real_tag}**!", ephemeral=True)
        else:
            await interaction.followup.send("[Error] Failed to save account link. Please try again later.", ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink your Valorant account from Discord")
    async def unlink(self, interaction: discord.Interaction) -> None:
        """Unlinks the user's Discord ID."""
        success = await self.api.unlink_user(interaction.user.id)
        if success:
            await interaction.response.send_message("[Success] Successfully unlinked your account.", ephemeral=True)
        else:
            await interaction.response.send_message("[Error] You don't have a linked account.", ephemeral=True)

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
        
        if name and tag:
            await interaction.response.defer()
            await process_and_send_stats(interaction, self.api, name, tag)
            return
            
        target = user or interaction.user
        link = await self.api.get_user_link(target.id)
        
        if link:
            await interaction.response.defer()
            await process_and_send_stats(interaction, self.api, link[0], link[1], region=link[2])
        elif user:
            await interaction.response.send_message(f"[Error] {user.display_name} has not linked their Valorant account yet.", ephemeral=True)
        else:
            await self._send_stat_intro(interaction)

    @commands.command(name="stat")
    async def stat_prefix(self, ctx: commands.Context) -> None:
        """Prefix command version with automatic lookup."""
        link = await self.api.get_user_link(ctx.author.id)
        if link:
            await process_and_send_stats(ctx, self.api, link[0], link[1], region=link[2])
        else:
            await self._send_stat_intro(ctx)

    async def _send_stat_intro(self, context: Union[discord.Interaction, commands.Context]) -> None:
        """Sends the initial interaction for stat lookup."""
        view = StatView(self.api, context.user.id if isinstance(context, discord.Interaction) else context.author.id)
        embed = discord.Embed(
            title="VALORANT TRACKER",
            description=(
                "> Directly retrieves data from Riot Games server.\n"
                "Please click the button below to start.\n\n"
                "**AVAILABLE DATA INCLUDES:**\n"
                "```yaml\n"
                "- Profile Level, Rank & Rank Rating (RR)\n"
                "- Kills/Deaths/Assists (K/D/A), Combat Score (ACS)\n"
                "- Results & Match History for the last 5 games\n"
                "```\n"
                "TIP: Use `/link` to connect your account and skip this step next time!"
            ),
            color=0xFD4553
        )
        embed.set_thumbnail(url="https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/24/largeicon.png")
        embed.set_image(url="https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt76953f937803e480/6234eff4093f413d727b14fc/032322_V_Ep4_Act3_Disruption_Social.jpg")
        embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url="https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/24/largeicon.png")

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view)
        else:
            await context.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
