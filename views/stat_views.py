import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union

import discord
from discord.ext import commands

from utils import ValorantAPI
from utils.i18n import t, DEFAULT_LANG


class PlayerStatsPagination(discord.ui.View):
    def __init__(self, p_embed: discord.Embed, m_embed: discord.Embed, owner_id: int, lang: str = DEFAULT_LANG) -> None:
        super().__init__(timeout=120)
        self.p_embed = p_embed
        self.m_embed = m_embed
        self.current = 0
        self.owner_id = owner_id
        self.lang = lang
        self.message: Optional[discord.Message] = None

        self.profile_btn = discord.ui.Button(label=t("btn_profile", lang), style=discord.ButtonStyle.primary)
        self.profile_btn.callback = self._show_profile
        self.add_item(self.profile_btn)

        self.history_btn = discord.ui.Button(label=t("btn_match_history", lang), style=discord.ButtonStyle.secondary)
        self.history_btn.callback = self._show_history
        self.add_item(self.history_btn)

    async def on_timeout(self) -> None:
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except (discord.NotFound, discord.HTTPException):
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(t("button_denied", self.lang), ephemeral=True)
            return False
        return True

    def _update_styles(self) -> None:
        if self.current == 0:
            self.profile_btn.style = discord.ButtonStyle.primary
            self.history_btn.style = discord.ButtonStyle.secondary
        else:
            self.profile_btn.style = discord.ButtonStyle.secondary
            self.history_btn.style = discord.ButtonStyle.primary

    async def _show_profile(self, interaction: discord.Interaction) -> None:
        if self.current == 0:
            await interaction.response.defer()
            return
        self.current = 0
        self._update_styles()
        await interaction.response.edit_message(embed=self.p_embed, view=self)

    async def _show_history(self, interaction: discord.Interaction) -> None:
        if self.current == 1:
            await interaction.response.defer()
            return
        self.current = 1
        self._update_styles()
        await interaction.response.edit_message(embed=self.m_embed, view=self)


async def process_and_send_stats(context: Union[discord.Interaction, commands.Context], api: ValorantAPI, name: str, tag: str, region: Optional[str] = None, lang: str = DEFAULT_LANG) -> None:
    """Core logic to fetch data and send the player stats embed."""
    
    is_interaction = isinstance(context, discord.Interaction)
    ref_msg = None

    loading_embed = discord.Embed(description=f"**{t('stat_loading', lang)}**", color=0xFD4553)
    if is_interaction:
        if not context.response.is_done():
            await context.response.defer()
        await context.edit_original_response(embed=loading_embed)
    else:
        ref_msg = await context.send(embed=loading_embed)

    async def update_response(**kwargs):
        """Edit the loading message with final content."""
        if is_interaction:
            await context.edit_original_response(**kwargs)
            view = kwargs.get('view')
            if view and hasattr(view, 'message'):
                try:
                    view.message = await context.original_response()
                except discord.HTTPException:
                    pass
        elif ref_msg:
            await ref_msg.edit(**kwargs)
            view = kwargs.get('view')
            if view and hasattr(view, 'message'):
                view.message = ref_msg

    if region:
        results = await asyncio.gather(
            api.get_account_info(name, tag),
            api.get_stats(name, tag, region=region),
            api.get_recent_matches(name, tag, region=region),
            return_exceptions=True
        )
        acc_data: Dict[str, Any] = results[0] if isinstance(results[0], dict) else {}
        mmr_data: Dict[str, Any] = results[1] if isinstance(results[1], dict) else {}
        matches_data: Dict[str, Any] = results[2] if isinstance(results[2], dict) else {}
    else:
        acc_data = await api.get_account_info(name, tag)
        if not acc_data or acc_data.get('status') != 200:
            error_msg = acc_data.get('message', 'Failed to connect to API.') if acc_data else 'API timeout.'
            error_embed = discord.Embed(
                description=t('stat_error_account', lang, name=name, tag=tag, error=error_msg),
                color=0xff4444
            )
            await update_response(embed=error_embed)
            return
        
        region = str(acc_data.get('data', {}).get('region', 'na')).lower()
        
        results = await asyncio.gather(
            api.get_stats(name, tag, region=region),
            api.get_recent_matches(name, tag, region=region),
            return_exceptions=True
        )
        mmr_data: Dict[str, Any] = results[0] if isinstance(results[0], dict) else {}
        matches_data: Dict[str, Any] = results[1] if isinstance(results[1], dict) else {}

    acc_inner = acc_data.get('data', {}) if acc_data.get('status') == 200 else {}
    level = str(acc_inner.get('account_level', '???'))
    
    card_dict = acc_inner.get('card', {})
    card_wide: Optional[str] = card_dict.get('large') if isinstance(card_dict, dict) else None
    card_small: Optional[str] = card_dict.get('small') if isinstance(card_dict, dict) else None
    
    if mmr_data.get('status') != 200:
        error_msg = mmr_data.get('message', 'Failed to retrieve rank data.')
        error_embed = discord.Embed(
            description=t('stat_error_rank', lang, name=name, tag=tag, error=error_msg),
            color=0xff4444
        )
        await update_response(embed=error_embed)
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
        title=t("title_match_history", lang, name=name, tag=tag),
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
            name=t("no_data", lang),
            value=f"```\n{t('stat_no_matches', lang)}\n```", 
            inline=False
        )
    
    matches_embed.set_footer(text="Inu Bot • Powered by HenrikDev API", icon_url=rank_icon)

    owner_id = context.user.id if isinstance(context, discord.Interaction) else context.author.id

    await update_response(
        embed=profile_embed,
        view=PlayerStatsPagination(profile_embed, matches_embed, owner_id, lang=lang)
    )


class StatModal(discord.ui.Modal):
    def __init__(self, api: ValorantAPI, lang: str = DEFAULT_LANG, intro_message: Optional[discord.Message] = None) -> None:
        super().__init__(title=t("stat_modal_title", lang))
        self.api = api
        self.lang = lang
        self.intro_message = intro_message

        self.name_input = discord.ui.TextInput(
            label=t("stat_modal_name", lang),
            placeholder=t("stat_modal_name_ph", lang),
            required=True,
            max_length=16
        )
        self.add_item(self.name_input)

        self.tag_input = discord.ui.TextInput(
            label=t("stat_modal_tag", lang),
            placeholder=t("stat_modal_tag_ph", lang),
            required=True,
            min_length=3,
            max_length=5
        )
        self.add_item(self.tag_input)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        name = self.name_input.value.strip()
        tag = self.tag_input.value.strip()
        await interaction.response.defer(ephemeral=False)
        # Clean up the intro message buttons
        if self.intro_message:
            try:
                await self.intro_message.edit(view=None)
            except (discord.NotFound, discord.HTTPException):
                pass
        await process_and_send_stats(interaction, self.api, name, tag, lang=self.lang)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        msg = f"[Error] {t('stat_modal_error', self.lang, error=str(error))}"
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            await interaction.followup.send(msg, ephemeral=True)


class StatView(discord.ui.View):
    def __init__(self, api: ValorantAPI, owner_id: int, lang: str = DEFAULT_LANG) -> None:
        super().__init__(timeout=300)
        self.api = api
        self.owner_id = owner_id
        self.lang = lang
        self.message: Optional[discord.Message] = None

        self.lookup_btn = discord.ui.Button(label=t("btn_lookup", lang), style=discord.ButtonStyle.primary)
        self.lookup_btn.callback = self._open_modal
        self.add_item(self.lookup_btn)

    async def on_timeout(self) -> None:
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except (discord.NotFound, discord.HTTPException):
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(t("button_denied", self.lang), ephemeral=True)
            return False
        return True

    async def _open_modal(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(StatModal(self.api, lang=self.lang, intro_message=self.message))
