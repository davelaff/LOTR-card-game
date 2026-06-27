"""
ASCII board renderer for the LOTR Card Battle Game.
"""

from engine.card import BoardAlly, CardType, Keyword
from engine.board import Board, LocationSlot
from engine.ring import Ring
from engine.player import PlayerState

def render_game_state(game) -> str:
    """Render the full game state as ASCII art."""
    lines = []
    fp = game.fp_player
    sh = game.shadow_player
    board = game.board
    ring = game.ring
    
    # Header
    active_name = "Free Peoples (Gondor)" if game.active_player == "fp" else "Shadow (Mordor)"
    lines.append("=" * 80)
    lines.append(f"  THE LORD OF THE RINGS: Digital Card Battle  |  Turn {fp.turn_number}  |  {game.current_phase}")
    lines.append(f"  Active: {active_name}")
    lines.append("=" * 80)
    
    # Player info bar
    fp_wp = f"WP:{fp.willpower_pool}/{fp.effective_willpower_max}"
    sh_wp = f"WP:{sh.willpower_pool}/{sh.effective_willpower_max}"
    fp_info = f"Gondor  |  Influence: {fp.influence:>2}  |  {fp_wp}  |  Hand: {fp.hand_size}  |  Deck: {fp.deck_size}"
    sh_info = f"Mordor  |  Influence: {sh.influence:>2}  |  {sh_wp}  |  Hand: {sh.hand_size}  |  Deck: {sh.deck_size}"
    
    lines.append(f"  {fp_info}")
    lines.append(f"  {sh_info}")
    
    # Ring status
    bearer = "Free Peoples" if ring.bearer == "fp" else "SHADOW"
    lines.append(f"  Ring: {bearer} bears the One Ring  |  {ring.corruption_track_str}")
    lines.append("")
    
    # Deployment zones
    lines.append(render_deployment_zone(board, "fp", "Free Peoples (Gondor)"))
    lines.append("            |")
    
    # Location row header
    lines.append("  " + " — ".join([
        f"[Slot {i+1}: {loc.location_card.name if loc.location_card else 'Empty'}]" 
        for i, loc in enumerate(board.locations)
    ]))
    lines.append("")
    
    # Each location front/back lines
    loc_lines = ["", "", ""]  # Three lines: FP front, FP back, loc divider, SH front, SH back
    
    fp_front_parts = []
    fp_back_parts = []
    sh_front_parts = []
    sh_back_parts = []
    
    for i, loc in enumerate(board.locations):
        width = 28
        
        # FP allies at this location
        fp_front = render_ally_list(loc.fp_front, width)
        fp_back = render_ally_list(loc.fp_back, width)
        sh_front = render_ally_list(loc.shadow_front, width)
        sh_back = render_ally_list(loc.shadow_back, width)
        
        fp_front_parts.append(fp_front)
        fp_back_parts.append(fp_back)
        sh_front_parts.append(sh_front)
        sh_back_parts.append(sh_back)
    
    # Render rows
    lines.append("        FP Front: " + " | ".join(fp_front_parts))
    lines.append("        FP Back:  " + " | ".join(fp_back_parts))
    lines.append("        " + "-" * 76)
    lines.append("        SH Front: " + " | ".join(sh_front_parts))
    lines.append("        SH Back:  " + " | ".join(sh_back_parts))
    
    lines.append("")
    lines.append("            |")
    lines.append(render_deployment_zone(board, "shadow", "Shadow (Mordor)"))
    lines.append("")
    
    # Hand display
    if game.active_player == "fp":
        lines.append(render_hand(fp, "Your"))
    lines.append("=" * 80)
    
    return "\n".join(lines)


def render_deployment_zone(board: Board, player: str, label: str) -> str:
    """Render a deployment zone."""
    zone = board.fp_deployment if player == "fp" else board.shadow_deployment
    allies = render_ally_list(zone, 60)
    return f"  [{label} Deployment: {allies}]"


def render_ally_list(allies: list, width: int) -> str:
    """Render a list of allies in compact form."""
    if not allies:
        return "—".center(width - 6)
    parts = []
    for a in allies:
        dmg = f"[{a.damage}dmg]" if a.damage > 0 else ""
        tap = " T" if a.tapped else ""
        art = " *" if a.artifacts else ""
        rng = " R" if a.has_ranged else ""
        parts.append(f"{a.card.name}({a.card.power}/{a.current_toughness}){dmg}{tap}{art}{rng}")
    return ", ".join(parts)


def render_hand(player: PlayerState, label: str) -> str:
    """Render the player's hand."""
    if not player.hand:
        return f"  {label} Hand: (empty)"
    
    lines = [f"  {label} Hand ({len(player.hand)} cards, {player.willpower_pool} WP available):"]
    for i, card in enumerate(player.hand):
        type_marker = ""
        if card.card_type == CardType.ALLY:
            type_marker = f" [Ally {card.power}/{card.toughness}]"
        elif card.card_type == CardType.EVENT:
            type_marker = " [Event]"
        elif card.card_type == CardType.ARTIFACT:
            type_marker = " [Artifact]"
        elif card.card_type == CardType.LOCATION:
            type_marker = f" [Location Def:{card.defense}]"
        
        kw = ""
        if card.keywords:
            kw = " {" + ", ".join(k.value for k in card.keywords) + "}"
        
        lines.append(f"    [{i+1}] {card.name} (Cost: {card.cost} WP){type_marker}{kw}")
        if card.rules_text:
            lines.append(f"        {card.rules_text[:80]}")
    
    return "\n".join(lines)


def render_messages(messages: list) -> str:
    """Render game messages."""
    if not messages:
        return ""
    return "\n".join(f"  > {m}" for m in messages[-10:])  # Last 10 messages


def render_action_menu(player: PlayerState, game) -> str:
    """Render the action menu for the active player."""
    lines = []
    lines.append("")
    lines.append("  ACTIONS:")
    lines.append(f"  [P#] Play card # from hand")
    lines.append(f"  [M]  Move an ally (to location or between rows)")
    lines.append(f"  [A]  Attack with an ally")
    lines.append(f"  [H]  Use Hero ability")
    lines.append(f"  [R]  Activate the Ring (once/turn)")
    lines.append(f"  [E]  End Main Phase / End Turn")
    lines.append(f"  [Q]  Quit game")
    lines.append("")
    lines.append(f"  WP Available: {player.willpower_pool}/{player.effective_willpower_max}")
    
    # Ring status
    if game.ring.bearer == game.active_player:
        activated = game.ring.fp_activated_this_turn if game.active_player == "fp" else game.ring.shadow_activated_this_turn
        if activated:
            lines.append("  Ring: Already activated this turn")
        else:
            lines.append("  Ring: Ready to activate")
    
    return "\n".join(lines)
