import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from typing import Optional, List, Dict, Any, Tuple, Union
from utils.riot_api import ValorantAPI

class StatModal(discord.ui.Modal, title='TRA CỨU CHỈ SỐ VALORANT'):
    def __init__(self, api: ValorantAPI) -> None:
        super().__init__()
        self.api = api

    name_input = discord.ui.TextInput(
        label='Tên In-game (Riot ID)',
        placeholder='Ví dụ: TenZ',
        required=True
    )
    tag_input = discord.ui.TextInput(
        label='Tag (không cần dấu #)',
        placeholder='Ví dụ: 0405',
        required=True,
        min_length=3,
        max_length=5
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        name = self.name_input.value
        tag = self.tag_input.value
        
        await interaction.response.defer(ephemeral=False)
        
        try:
            # Gather data concurrently
            acc_data, mmr_data, matches_data = await asyncio.gather(
                self.api.get_account_info(name, tag),
                self.api.get_stats(name, tag),
                self.api.get_recent_matches(name, tag),
                return_exceptions=True
            )
            
            if isinstance(mmr_data, Exception) or not mmr_data or mmr_data.get('status') != 200:
                await interaction.followup.send(f"❌ Không tìm thấy người chơi **{name}#{tag}** hoặc tài khoản đang ở chế độ riêng tư.", ephemeral=True)
                return

            data = mmr_data.get('data', {})
            rank = data.get('currenttierpatched', 'Unrated')
            rr = data.get('ranking_in_tier', 0)
            rank_color, rank_icon = self.api.get_rank_assets(rank)
            
            # Progress bar
            bars = int(rr / 10)
            progress_bar = f"`{'▰' * bars}{'▱' * (10 - bars)}` **{rr}/100 RR**"
            
            level = "???"
            card_wide = None
            card_small = None
            region = data.get('region', 'N/A').upper()
            
            if isinstance(acc_data, dict) and acc_data.get('status') == 200:
                acc_info = acc_data.get('data', {})
                level = acc_info.get('account_level', '???')
                card_wide = acc_info.get('card', {}).get('wide') 
                card_small = acc_info.get('card', {}).get('small')

            # --- Embed 1: Profile ---
            profile_embed = discord.Embed(
                title=f"🏆 {name}#{tag}",
                description=f"**{rank}**\n{progress_bar}",
                color=rank_color
            )
            profile_embed.set_thumbnail(url=rank_icon)
            profile_embed.set_author(name=f"Level {level} • Region: {region}", icon_url=card_small)
            if card_wide:
                profile_embed.set_image(url=card_wide)
            
            # --- Recent Matches Summary (Monospace for alignment) ---
            match_stats = "```\n"
            match_stats += f"{'MODE':<12} | {'RESULT':<7} | {'K/D/A':<10}\n"
            match_stats += "-" * 35 + "\n"

            if isinstance(matches_data, dict) and matches_data.get('status') == 200:
                for m in matches_data['data']:
                    meta = m.get('metadata', {})
                    mode = meta.get('mode', 'Unknown')
                    
                    p = next((p for p in m['players']['all_players'] if p['name'].lower() == name.lower()), None)
                    if p:
                        k, d, a = p['stats']['kills'], p['stats']['deaths'], p['stats']['assists']
                        team = p['team'].lower()
                        is_win = m['teams'].get(team, {}).get('has_won', False)
                        result = "WIN" if is_win else "LOSS"
                        match_stats += f"{mode[:12]:<12} | {result:<7} | {k}/{d}/{a}\n"
            else:
                match_stats += "No recent matches found.\n"
            
            match_stats += "```"
            profile_embed.add_field(name="Recent Matches", value=match_stats, inline=False)
            profile_embed.set_footer(text="Inu Bot • Premium Analytics", icon_url=interaction.user.display_avatar.url)
            
            await interaction.followup.send(embed=profile_embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Có lỗi xảy ra: {str(e)}", ephemeral=True)

class StatView(discord.ui.View):
    def __init__(self, api: ValorantAPI) -> None:
        super().__init__(timeout=None)
        self.api = api

    @discord.ui.button(label="Tra cứu ngay", style=discord.ButtonStyle.success, emoji="📊", custom_id="stat_lookup_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(StatModal(self.api))

class StatsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.api: ValorantAPI = getattr(bot, 'v_api')

    @app_commands.command(name="stat", description="Tra cứu chỉ số Valorant của người chơi")
    async def stat_slash(self, interaction: discord.Interaction) -> None:
        """Slash command version of stat"""
        await self._send_stat_intro(interaction)

    @commands.command(name="stat")
    async def stat_prefix(self, ctx: commands.Context) -> None:
        """Prefix command version of stat"""
        await self._send_stat_intro(ctx)

    async def _send_stat_intro(self, context: Union[discord.Interaction, commands.Context]) -> None:
        """Mở bảng tra cứu chỉ số Valorant giao diện Premium"""
        view = StatView(self.api)
        embed = discord.Embed(
            title="VALORANT TRACKER",
            description=(
                "Chào mừng bạn đến với hệ thống theo dõi Valorant.\n\n"
                "Nhấn nút bên dưới để xem:\n"
                "• **Rank & RR hiện tại**\n"
                "• **Lịch sử 3 trận đấu mới nhất**\n"
                "• **Chỉ số K/D/A chi tiết**"
            ),
            color=0xFD4553
        )
        embed.set_image(url="https://images.contentstack.io/v3/assets/bltb6530b271fddd0b1/blt76953f937803e480/6234eff4093f413d727b14fc/032322_V_Ep4_Act3_Disruption_Social.jpg")
        embed.set_footer(text="Hệ thống tra cứu thời gian thực")

        if isinstance(context, discord.Interaction):
            await context.response.send_message(embed=embed, view=view)
        else:
            await context.send(embed=embed, view=view)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatsCog(bot))
