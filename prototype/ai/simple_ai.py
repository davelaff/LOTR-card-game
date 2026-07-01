"""
Simple AI for the Shadow opponent.
Uses basic heuristics for card play, movement, and combat.
Works with any faction (not just Mordor).
"""

import random
from engine.card import CardType, BoardAlly, Keyword, Faction
from engine.game import GameState


class SimpleAI:
    """Basic heuristic AI for Shadow factions."""
    
    def __init__(self, game: GameState):
        self.game = game
    
    def take_turn(self) -> list:
        """Execute a full turn for the AI. Returns messages."""
        msgs = []
        
        if self.game.current_phase != "Main Phase":
            return msgs
        
        player_state = self.game.shadow_player
        board = self.game.board
        
        # Priority 1: Play cards if we have WP
        msgs.extend(self._play_cards(player_state))
        
        # Priority 2: Move allies to locations (from deployment)
        msgs.extend(self._move_allies(player_state))
        
        # Priority 3: Attack with available allies
        msgs.extend(self._attack(player_state))
        
        # Priority 4: Try Ring activation if Shadow bears it
        if self.game.ring.bearer == "shadow" and self.game.ring.can_activate_shadow():
            msgs.extend(self._activate_ring())
        
        # Priority 5: Use Hero ability
        hero = player_state.hero
        if hero and not hero.tapped and not hero.has_used_ability_this_turn:
            msgs.extend(self._use_hero_ability(player_state))
        
        # End turn
        self.game.end_turn()
        msgs.append("AI ends its turn.")
        
        return msgs
    
    def _play_cards(self, player_state) -> list:
        """Play affordable cards using heuristics."""
        msgs = []
        hand = list(player_state.hand)
        
        played = 0
        for card in hand:
            if played >= 5:
                break
            if card.cost > player_state.willpower_pool:
                continue
            
            # Skip only very expensive cards if WP is tight
            if card.cost >= 7 and player_state.willpower_pool < 8:
                continue
            
            result = self.game.play_card(card, "shadow")
            msgs.extend(result)
            if "Played" in " ".join(result):
                played += 1
                player_state = self.game.shadow_player
        
        return msgs
    
    def _move_allies(self, player_state) -> list:
        """Move allies from deployment to locations."""
        msgs = []
        board = self.game.board
        
        # Move from deployment to locations
        zone = board.shadow_deployment
        moved = 0
        for ally in list(zone):
            if ally.tapped:
                continue
            if moved >= 2:
                break
            
            # Prefer center location first, prefer contested
            target_loc = 1  # Default center
            for loc_idx in [1, 0, 2]:
                loc = board.get_location(loc_idx)
                if loc.is_empty():
                    continue  # Skip if no location card
                # Prefer contested locations
                if loc.is_contested():
                    target_loc = loc_idx
                    break
                if loc.controller == "shadow" or loc.controller is None:
                    target_loc = loc_idx
            
            row = "front"
            loc = board.get_location(target_loc)
            if len(loc.shadow_front) >= 3:
                row = "back"
            
            result = self.game.move_ally(ally, "shadow", target_loc, row)
            msgs.extend(result)
            moved += 1
        
        # Move hero from deployment
        hero = player_state.hero
        if hero:
            hero_loc = board.find_ally_location(hero, "shadow")
            if hero_loc == -1:
                result = self.game.move_ally(hero, "shadow", 0, "front")
                msgs.extend(result)
        
        return msgs
    
    def _attack(self, player_state) -> list:
        """Attack with available allies."""
        msgs = []
        board = self.game.board
        enemy = "fp"
        attacks_made = 0
        
        for loc_idx, loc in enumerate(board.locations):
            attackers = []
            for ally in loc.get_allies("shadow"):
                if ally.can_attack(player_state.turn_number):
                    targets = loc.valid_attack_targets(ally, "shadow")
                    if targets:
                        attackers.append((ally, targets))
            
            for attacker, targets in attackers:
                if not targets:
                    continue
                
                # Choose target: prefer weakest enemy ally
                best_target = None
                best_type = None
                best_toughness = 999
                
                for t_type, target in targets:
                    if t_type != "location":
                        if target.current_toughness < best_toughness:
                            best_toughness = target.current_toughness
                            best_target = target
                            best_type = t_type
                
                # If no ally targets, attack location
                if best_target is None:
                    for t_type, target in targets:
                        if t_type == "location":
                            best_target = target
                            best_type = t_type
                            break
                
                if best_target is None:
                    continue
                
                # Resolve attack
                result = self.game.combat.resolve_attack(
                    attacker, "shadow", best_target, best_type
                )
                msgs.extend(result["messages"])
                attacks_made += 1
                
                # Handle destruction
                if result.get("target_destroyed") and best_type in ("ally_front", "ally_back"):
                    board.remove_ally(best_target, enemy)
                    self.game.fp_player.discard.append(best_target.card)
                    
                    # Death triggers
                    death_msgs = self.game.effects.resolve_on_destroy(best_target, enemy)
                    msgs.extend(death_msgs)
                    
                    # Check hero destruction
                    if best_target is self.game.fp_player.hero:
                        self.game.fp_player.hero = None
                        self.game.fp_player.hero_in_play = False
                        self.game.fp_player.leaderless = True
                        msgs.append(f"{best_target.card.name} has fallen!")
                        
                        if self.game.ring.bearer == "fp":
                            self.game.ring.steal_by_shadow()
                            msgs.append("*** The Ring has been seized by the Shadow! ***")
                
                # Check location flip
                if result.get("location_flipped"):
                    msgs.append(f"Location flipped to Shadow control!")
                
                # Attack limit: 5 attacks total per turn
                if attacks_made >= 5:
                    return msgs
            
            # Check game over after each location
            self.game._check_game_over()
            if self.game.game_over:
                break
        
        return msgs
    
    def _activate_ring(self) -> list:
        """Activate the Ring under Shadow dominion."""
        msgs = []
        if self.game.fp_player.willpower_pool >= 2:
            choice = "drain"
        elif self.game.ring.corruption < 15:
            choice = "corrupt"
        else:
            choice = "fortify"
        
        return self.game.effects.resolve_ring_activation_shadow(choice)
    
    def _use_hero_ability(self, player_state) -> list:
        """Use the hero's activated ability. Faction-aware."""
        msgs = []
        hero = player_state.hero
        if not hero:
            return msgs
        
        faction = player_state.faction
        loc_index = self.game.board.find_ally_location(hero, "shadow")
        if loc_index is None or loc_index < 0:
            return msgs  # Hero must be at a location
        
        loc = self.game.board.get_location(loc_index)
        
        # --- Mordor: Gothmog — The Swarm Rises ---
        if faction == Faction.MORDOR and player_state.willpower_pool >= 2:
            if player_state.spend_willpower(2):
                from engine.effects import create_orc_token
                token = create_orc_token()
                token_ally = BoardAlly(
                    card=token,
                    current_toughness=token.toughness,
                    turn_entered=player_state.turn_number,
                )
                loc.add_ally(token_ally, "shadow", "front")
                msgs.append(f"{hero.card.name} creates an Orc token!")
                hero.has_used_ability_this_turn = True
        
        # --- Isengard: Saruman — The Voice of Saruman ---
        elif faction == Faction.ISENGARD and loc.is_contested():
            # Debuff an enemy at this location
            fp_allies = loc.get_allies("fp")
            if fp_allies:
                # Debuff the strongest enemy
                target = max(fp_allies, key=lambda a: a.effective_power)
                msgs.append(f"Saruman's voice weakens {target.card.name}! (-2 Power)")
                hero.tapped = True
                hero.has_used_ability_this_turn = True
        
        # --- Moria: Gorbag — Ambush Commander ---
        elif faction == Faction.MORIA and player_state.willpower_pool >= 2:
            # Find a Goblin in hand to deploy
            goblin = None
            for card in player_state.hand:
                if card.card_type == CardType.ALLY and "Goblin" in card.creature_types:
                    goblin = card
                    break
            if goblin and player_state.spend_willpower(2):
                player_state.play_card(goblin)
                ally = BoardAlly(
                    card=goblin,
                    current_toughness=goblin.toughness,
                    turn_entered=player_state.turn_number,
                )
                # Deploy directly to a contested or enemy location
                target_loc = loc
                for l in self.game.board.locations:
                    if l.is_contested():
                        target_loc = l
                        break
                target_loc.add_ally(ally, "shadow", "front")
                msgs.append(f"Gorbag deploys {goblin.name} via Ambush!")
                hero.has_used_ability_this_turn = True
        
        # --- Harad: The Golden King — Serpent-lord ---
        elif faction == Faction.HARAD and not hero.has_used_ability_this_turn:
            player_state.add_willpower(2)
            msgs.append(f"The Golden King grants +2 Willpower! (now {player_state.willpower_pool})")
            hero.tapped = True
            hero.has_used_ability_this_turn = True
        
        # --- Nazgul: Witch-king — Morgul-blade (once/game) ---
        elif faction == Faction.NAZGUL and not hero.has_used_ability_this_turn:
            fp_allies = loc.get_allies("fp")
            if fp_allies:
                target = fp_allies[0]
                target.take_damage(4)
                msgs.append(f"Witch-king strikes {target.card.name} with the Morgul-blade! (4 damage, cannot heal)")
                hero.tapped = True
                hero.has_used_ability_this_turn = True
        
        # Generic: exhaust hero for basic effect
        elif not hero.has_used_ability_this_turn:
            msgs.append(f"{hero.card.name} uses ability (generic).")
            hero.tapped = True
            hero.has_used_ability_this_turn = True
        
        return msgs
