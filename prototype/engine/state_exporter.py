"""
State exporter — serializes GameState to a JSON-serializable dict
consumed by the browser renderer (ui/browser_renderer.py).
"""
from typing import Any
from engine.game import GameState


def export_state(game: GameState) -> dict[str, Any]:
    """Convert the full GameState into a dict for the browser renderer."""
    board = game.board
    ring = game.ring

    def player_dict(ps, player: str) -> dict:
        """Serialize one PlayerState."""
        hand_cards = []
        for card in ps.hand:
            entry: dict = {
                "name": card.name,
                "cost": card.cost,
                "type": card.card_type.value,
                "rules": card.rules_text[:60] if card.rules_text else "",
            }
            if hasattr(card, "power") and card.power is not None:
                entry["power"] = card.power
            if hasattr(card, "toughness") and card.toughness is not None:
                entry["toughness"] = card.toughness
            hand_cards.append(entry)

        hero_data = None
        if ps.hero:
            hero_data = {
                "name": ps.hero.card.name,
                "power": ps.hero.card.power,
                "toughness": ps.hero.current_toughness,
                "tapped": ps.hero.tapped,
                "img": f"ui/assets/heroes/{ps.faction.value.lower()}.png" if ps.faction else None,
            }

        return {
            "faction": ps.faction.value if ps.faction else "Unknown",
            "influence": ps.influence,
            "willpower_pool": ps.willpower_pool,
            "willpower_max": ps.effective_willpower_max,
            "hand": hand_cards,
            "deck_size": len(ps.deck),
            "hero": hero_data,
            "leaderless": ps.leaderless,
        }

    def ally_str(ally, faction) -> str:
        """Format an ally as 'Name(P/T)' string for the board display."""
        name = ally.card.name
        p = ally.effective_power
        t = ally.current_toughness
        return f"{name}({p}/{t})"

    def location_dict(loc, fp_faction, sh_faction) -> dict:
        """Serialize one LocationSlot."""
        controller = loc.controller  # "fp", "shadow", or None

        fp_front = [ally_str(a, fp_faction) for a in loc.get_front_line("fp")]
        fp_back = [ally_str(a, fp_faction) for a in loc.get_back_line("fp")]
        sh_front = [ally_str(a, sh_faction) for a in loc.get_front_line("shadow")]
        sh_back = [ally_str(a, sh_faction) for a in loc.get_back_line("shadow")]

        return {
            "name": loc.location_card.name if loc.location_card else "Empty",
            "defense": loc.current_defense,
            "controller": controller,
            "fp_front": fp_front,
            "fp_back": fp_back,
            "shadow_front": sh_front,
            "shadow_back": sh_back,
        }

    fp_faction = game.fp_player.faction
    sh_faction = game.shadow_player.faction

    locs = [location_dict(loc, fp_faction, sh_faction) for loc in board.locations]

    return {
        "fp_player": player_dict(game.fp_player, "fp"),
        "shadow_player": player_dict(game.shadow_player, "shadow"),
        "board": {"locations": locs},
        "ring": {
            "corruption": ring.corruption,
            "bearer": ring.bearer,
        },
        "active_player": game.active_player,
        "turn_number": game.fp_player.turn_number,
        "phase": game.current_phase,
    }
