import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union

import discord
from discord.ext import commands

from utils import ValorantAPI


class PlayerStatsPagination(discord.ui.View):
    def __init__(self, p_embed: discord.Embed, m_embed: discord.Embed) -> None:
        super().__init__(timeout=120)
        self.p_embed = p_embed
        self.m_embed = m_embed
        self.current = 0

    @discord.ui.button(label="MATCH HISTORY", style=discord.ButtonStyle.primary)
    async def navigate(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.current == 0:
            self.current = 1
            button.label = "PROFILE"
            await interaction.response.edit_message(embed=self.m_embed, view=self)
        else:
            self.current = 0
            button.label = "MATCH HISTORY"
            await interaction.response.edit_message(embed=self.p_embed, view=self)


async def process_and_send_stats(context: Union[discord.Interaction, commands.Context], api: ValorantAPI, name: str, tag: str) -> None:
    """Core logic to fetch data and send the player stats embed."""
    
    async def send_response(content: str = None, embed: discord.Embed = None, view: discord.ui.View = None, ephemeral: bool = False):
        if isinstance(context, discord.Interaction):
            if context.response.is_done():
                await context.followup.send(content=content, embed=embed, view=view, ephemeral=ephemeral)
            else:
                await context.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)
        else:
            await context.send(content=content, embed=embed, view=view)

    acc_data = await api.get_account_info(name, tag)
    if not acc_data or acc_data.get('status') != 200:
        error_msg = acc_data.get('message', 'Failed to connect to API.') if acc_data else 'API timeout.'
        await send_response(
            content=f"[Error] Could not find account **{name}#{tag}**.\nDetails: {error_msg}", 
            ephemeral=True
        )
        return
        
    acc_inner = acc_data.get('data', {})
    region = str(acc_inner.get('region', 'na')).lower()
    level = str(acc_inner.get('account_level', '???'))
    
    card_dict = acc_inner.get('card', {})
    card_wide: Optional[str] = card_dict.get('large') if isinstance(card_dict, dict) else None
    card_small: Optional[str] = card_dict.get('small') if isinstance(card_dict, dict) else None
    
    results = await asyncio.gather(
        api.get_stats(name, tag, region=region),
        api.get_recent_matches(name, tag, region=region),
        return_exceptions=True
    )
    
    mmr_data: Dict[str, Any] = results[0] if isinstance(results[0], dict) else {}
    matches_data: Dict[str, Any] = results[1] if isinstance(results[1], dict) else {}
    
    if mmr_data.get('status') != 200:
        error_msg = mmr_data.get('message', 'Failed to retrieve rank data.')
        await send_response(
            content=f"[Error] Could not find rank data for **{name}#{tag}**.\nDetails: {error_msg}\n*Ensure the player has played at least 1 recent competitive match.*", 
            ephemeral=True
        )
        return

    mmr_full = mmr_data.get('data', {})
    mmr_inner = mmr_full.get('current', {})
    tier_dict = mmr_inner.get('tier', {})
    rank = str(tier_dict.get('name', 'Unrated'))
    rr = int(mmr_inner.get('rr', 0))
    rank_color, rank_icon = api.get_rank_assets(rank)
    
    peak_data = mmr_full.get('peak', {})
    peak_tier = peak_data.get('tier', {})
    peak_rank = str(peak_tier.get('name', 'Unknown'))
    
    rank_lower = rank.lower()
    if "radiant" in rank_lower or "immortal" in rank_lower or "unrated" in rank_lower:
        progress_bar = f"**{rr} RR**"
    else:
        bars = min(max(rr // 10, 0), 10)
        progress_bar = f"`{'▰' * bars}{'▱' * (10 - bars)}` **{rr}/100 RR**"
    
    desc_lines = f"**Rank:** {rank}\n{progress_bar}"
    if peak_rank.lower() not in ("unknown", "unrated"):
        _, peak_icon = api.get_rank_assets(peak_rank)
        desc_lines += f"\n\n**Peak Rank:** {peak_rank}"
    
    profile_embed = discord.Embed(
        title=f"{name}#{tag}",
        description=desc_lines,
        color=rank_color
    )
    profile_embed.set_thumbnail(url=rank_icon)
    profile_embed.set_author(name=f"Level: {level} | Region: {region.upper()}", icon_url=card_small)
    
    if card_wide:
        profile_embed.set_image(url=card_wide)
        
    profile_embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url=rank_icon)
    
    match_entries: List[Dict[str, Any]] = []
    if matches_data.get('status') == 200:
        matches_list = matches_data.get('data', [])
        for m in matches_list:
            if not isinstance(m, dict):
                continue
            
            meta = m.get('metadata', {})
            mode = str(meta.get('mode', 'Unknown'))
            map_name = str(meta.get('map', 'Unknown'))
            rounds = meta.get('rounds_played', 1)
            
            if not mode or mode.strip() in ["-", "--"]:
                continue
            
            players_dict = m.get('players', {})
            if not isinstance(players_dict, dict):
                continue
                
            all_players = players_dict.get('all_players', [])
            if not isinstance(all_players, list):
                continue
                
            p = next(
                (
                    player for player in all_players 
                    if isinstance(player, dict) 
                    and player.get('name', '').lower() == name.lower()
                    and player.get('tag', '').lower() == tag.lower()
                ), 
                None
            )
            
            if p:
                st = p.get('stats', {})
                if not isinstance(st, dict):
                    st = {}
                    
                k = st.get('kills', 0)
                d = st.get('deaths', 0)
                a = st.get('assists', 0)
                score = st.get('score', 0)
                headshots = st.get('headshots', 0)
                bodyshots = st.get('bodyshots', 0)
                legshots = st.get('legshots', 0)
                
                total_shots = headshots + bodyshots + legshots
                hs_pct = round((headshots / total_shots) * 100) if total_shots > 0 else 0
                
                try:
                    acs = round(int(score) / int(rounds)) if int(rounds) > 0 else 0
                except (ValueError, TypeError):
                    acs = 0
                
                agent = str(p.get('character', 'Unknown'))
                
                team = str(p.get('team', 'Unknown')).lower()
                teams_dict = m.get('teams', {})
                
                is_win = False
                if isinstance(teams_dict, dict):
                    team_data = teams_dict.get(team, {})
                    if isinstance(team_data, dict):
                        is_win = team_data.get('has_won', False)
                
                match_entries.append({
                    'mode': mode,
                    'map': map_name,
                    'agent': agent,
                    'is_win': is_win,
                    'k': k, 'd': d, 'a': a,
                    'acs': acs,
                    'hs_pct': hs_pct
                })

    matches_embed = discord.Embed(
        title=f"MATCH HISTORY — {name}#{tag}",
        color=rank_color
    )
    matches_embed.set_thumbnail(url=rank_icon)
    
    if match_entries:
        for entry in match_entries:
            result_text = "[W]" if entry['is_win'] else "[L]"
            field_title = f"{result_text} {entry['mode']} — {entry['map']}"
            field_value = (
                f"```\n"
                f"Agent : {entry['agent']}\n"
                f"K/D/A : {entry['k']}/{entry['d']}/{entry['a']}\n"
                f"ACS   : {entry['acs']}  |  HS% : {entry['hs_pct']}%\n"
                f"```"
            )
            matches_embed.add_field(name=field_title, value=field_value, inline=False)
    else:
        matches_embed.add_field(
            name="No Data", 
            value="```\nNo recent matches found.\n```", 
            inline=False
        )
    
    matches_embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url=rank_icon)

    await send_response(
        embed=profile_embed, 
        view=PlayerStatsPagination(profile_embed, matches_embed)
    )


class StatModal(discord.ui.Modal, title='VALORANT STATS LOOKUP'):
    name_input = discord.ui.TextInput(
        label='In-game Name (Riot ID)',
        placeholder='Example: inu inu',
        required=True,
        max_length=16
    )
    tag_input = discord.ui.TextInput(
        label='Tagline (without #)',
        placeholder='Example: 2804',
        required=True,
        min_length=3,
        max_length=5
    )

    def __init__(self, api: ValorantAPI) -> None:
        super().__init__()
        self.api = api

    async def on_submit(self, interaction: discord.Interaction) -> None:
        name = self.name_input.value.strip()
        tag = self.tag_input.value.strip()
        await interaction.response.defer(ephemeral=False)
        await process_and_send_stats(interaction, self.api, name, tag)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        msg = f"[Error] An error occurred: `{str(error)}`"
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)


class StatView(discord.ui.View):
    def __init__(self, api: ValorantAPI) -> None:
        super().__init__(timeout=300)
        self.api = api

    @discord.ui.button(label="LOOKUP NOW", style=discord.ButtonStyle.danger, custom_id="stat_lookup_btn")
    async def open_modal(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_modal(StatModal(self.api))
