"""
Combat resolution for the LOTR Card Battle Game.
Attacker-directed combat with persistent damage.
"""

from typing import Optional, Callable
from engine.card import BoardAlly, CardType, Keyword
from engine.board import LocationSlot

class CombatResolver:
    """Handles combat resolution between attacker and target."""
    
    def __init__(self, game):
        self.game = game
    
    def resolve_attack(self, attacker: BoardAlly, attacker_player: str,
                       target, target_type: str) -> dict:
        """
        Resolve an attack. 
        target_type can be: "ally_front", "ally_back", or "location"
        Returns a dict describing what happened.
        """
        result = {
            "attacker": repr(attacker),
            "damage_dealt": 0,
            "target_destroyed": False,
            "trample_damage": 0,
            "location_flipped": False,
            "messages": [],
        }
        
        # Calculate damage
        base_power = attacker.card.power
        
        # Apply modifiers
        damage = base_power
        
        # Brutal: +1 damage
        if attacker.has_brutal:
            damage += 1
        
        # Check for fear effects (reduce power at same location)
        target_player = "shadow" if attacker_player == "fp" else "fp"
        if target_type in ("ally_front", "ally_back"):
            # Find location
            loc_index = self.game.board.find_ally_location(attacker, attacker_player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                # Apply fear auras from enemy allies at that location
                for enemy_ally in loc.get_allies(target_player):
                    if Keyword.FEAR in enemy_ally.card.keywords:
                        # Fear reduces power
                        damage = max(0, damage - 1)  # Simplified: each Fear reduces by 1
        
        result["damage_dealt"] = damage
        
        if target_type == "location":
            # Attack the location — or bypass to Influence if undefended
            target_slot = target
            enemy = "shadow" if attacker_player == "fp" else "fp"
            enemy_allies_at_loc = target_slot.get_allies(enemy)
            
            if not enemy_allies_at_loc:
                # Undefended location — damage goes directly to Influence
                enemy_state = self.game.shadow_player if attacker_player == "fp" else self.game.fp_player
                enemy_state.deal_influence_damage(damage)
                result["damage_dealt"] = damage
                result["messages"].append(
                    f"{target_slot.location_card.name} is undefended! {damage} damage to "
                    f"{'Shadow' if enemy == 'shadow' else 'Free Peoples'} Influence!"
                )
            else:
                # Defended — damage goes to location defense
                flipped = target_slot.deal_defense_damage(damage)
                result["location_flipped"] = flipped
                if flipped:
                    result["messages"].append(
                        f"{target_slot.location_card.name} flips to "
                        f"{'Free Peoples' if target_slot.controller == 'fp' else 'Shadow'} control!"
                    )
                else:
                    result["messages"].append(
                        f"Location {target_slot.location_card.name} takes {damage} damage "
                        f"(Def {target_slot.current_defense} remaining)."
                    )
        else:
            # Attack an ally
            target_ally = target
            excess = 0
            
            # Trample calculation
            if attacker.has_trample:
                if damage > target_ally.current_toughness:
                    excess = damage - target_ally.current_toughness
            
            # Apply persistent damage
            target_ally.take_damage(damage)
            result["messages"].append(
                f"{target_ally.card.name} takes {damage} damage "
                f"(Toughness: {target_ally.current_toughness}/{target_ally.card.toughness})."
            )
            
            # Check destruction
            if target_ally.current_toughness <= 0:
                result["target_destroyed"] = True
                result["messages"].append(
                    f"{target_ally.card.name} is destroyed!"
                )
                
                # Check if Ring-bearer was killed
                if attacker_player == "shadow" and \
                   self.game.fp_player.hero and target_ally is self.game.fp_player.hero:
                    result["messages"].append("*** THE RING IS SEIZED BY THE SHADOW! ***")
                elif attacker_player == "fp" and \
                     self.game.shadow_player.hero and target_ally is self.game.shadow_player.hero:
                    if self.game.ring.bearer == "shadow":
                        result["messages"].append("*** THE RING IS RECOVERED BY THE FREE PEOPLES! ***")
            
            # Handle trample damage to Influence
            if excess > 0:
                result["trample_damage"] = excess
                target_player_state = self.game.shadow_player if attacker_player == "fp" else self.game.fp_player
                target_player_state.deal_influence_damage(excess)
                result["messages"].append(
                    f"Trample: {excess} excess damage to Influence!"
                )
        
        # Attacker becomes tapped
        attacker.tapped = True
        attacker.has_attacked_this_turn = True
        
        return result
