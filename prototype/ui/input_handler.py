"""
Input handler for the LOTR Card Battle Game CLI.
"""

from typing import Optional
from engine.card import CardType, BoardAlly
from engine.game import GameState

class InputHandler:
    """Handles parsing and executing player commands."""
    
    def __init__(self, game: GameState):
        self.game = game
    
    def process_command(self, cmd: str) -> list:
        """Process a command string. Returns list of messages."""
        cmd = cmd.strip().upper()
        msgs = []
        
        if cmd == "Q" or cmd == "QUIT":
            msgs.append("Quitting game.")
            self.game.game_over = True
            return msgs
        
        if self.game.game_over:
            msgs.append("Game is over!")
            return msgs
        
        player = self.game.active_player
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        
        if cmd == "E" or cmd == "END":
            self.game.end_turn()
            return ["Ending turn..."]
        
        if cmd == "R":
            if player == "fp":
                return self._handle_ring_activation_fp()
            else:
                return self._handle_ring_activation_shadow()
        
        if cmd == "H":
            return self._handle_hero_ability()
        
        if cmd == "M":
            return self._handle_move()
        
        if cmd == "A":
            return self._handle_attack()
        
        if cmd.startswith("P"):
            # Play card
            try:
                num_str = cmd[1:].strip()
                idx = int(num_str) - 1
                return self._handle_play_card(idx)
            except (ValueError, IndexError):
                msgs.append(f"Invalid card number: {cmd}")
                return msgs
        
        msgs.append(f"Unknown command: {cmd}")
        return msgs
    
    def _handle_play_card(self, index: int) -> list:
        """Handle playing a card from hand."""
        msgs = []
        player = self.game.active_player
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        
        if index < 0 or index >= len(player_state.hand):
            msgs.append(f"Invalid card index (1-{len(player_state.hand)}).")
            return msgs
        
        card = player_state.hand[index]
        
        if card.cost > player_state.willpower_pool:
            msgs.append(f"Not enough Willpower! Need {card.cost}, have {player_state.willpower_pool}.")
            return msgs
        
        result = self.game.play_card(card, player)
        return result
    
    def _handle_ring_activation_fp(self) -> list:
        """Handle Free Peoples Ring activation."""
        print("\n  Ring Activation Options:")
        print("    [1] Draw 2 cards")
        print("    [2] Gain +2 Willpower this turn")
        print("    [3] Grant Stealth to Ring-bearer")
        print("    [4] Bolster location (+2 Defense)")
        
        choice = input("  Choose [1-4] or [C]ancel > ").strip()
        if choice.upper() == "C":
            return ["Ring activation cancelled."]
        
        choice_map = {"1": "draw", "2": "willpower", "3": "stealth", "4": "bolster"}
        if choice in choice_map:
            return self.game.effects.resolve_ring_activation_fp(choice_map[choice])
        return ["Invalid Ring choice. Use 1-4 or C."]
    
    def _handle_ring_activation_shadow(self) -> list:
        """Handle shadow ring activation (for AI, but available)."""
        # The player doesn't control shadow Ring in normal play,
        # but this is here for completeness
        return ["Shadow Ring activation handled by AI."]
    
    def _handle_hero_ability(self) -> list:
        """Handle hero ability activation."""
        player = self.game.active_player
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        hero = player_state.hero
        
        if not hero:
            return ["No hero available!"]
        
        if hero.tapped:
            return [f"{hero.card.name} is already tapped!"]
        
        if hero.has_used_ability_this_turn:
            return [f"{hero.card.name} has already used their ability this turn!"]
        
        return self.game.effects.resolve_hero_ability(hero, player)
    
    def _handle_move(self) -> list:
        """Handle moving an ally."""
        msgs = []
        player = self.game.active_player
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        board = self.game.board
        
        # Find movable allies
        movable = []
        for i, loc in enumerate(board.locations):
            for ally in loc.get_allies(player):
                if ally.can_move():
                    movable.append((i, loc.find_ally_row(ally, player), ally))
        # Also deployment zone
        zone = board.fp_deployment if player == "fp" else board.shadow_deployment
        for ally in zone:
            if not ally.tapped:
                movable.append((-1, "deployment", ally))
        # Hero is already covered by the location and deployment loops above
        # — no separate hero block needed
        
        if not movable:
            return ["No allies available to move! (Allies have summoning sickness on the turn they enter, and cannot both move and attack.)"]

        print("\n  Movable allies:")
        for j, (loc_idx, row, ally) in enumerate(movable):
            loc_name = f"Loc {loc_idx+1}" if loc_idx >= 0 else "Deployment"
            print(f"    [{j+1}] {ally.card.name} at {loc_name} ({row})")
        
        choice = input("  Choose ally number or [C]ancel > ").strip()
        if choice.upper() == "C":
            return ["Move cancelled."]
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(movable):
                return ["Invalid choice."]
        except ValueError:
            return ["Invalid input."]
        
        loc_idx, row, ally = movable[idx]
        
        # Choose destination
        print("\n  Move to which location?")
        for i in range(3):
            loc = board.get_location(i)
            loc_name = loc.location_card.name if loc.location_card else "Empty"
            print(f"    [{i+1}] Location {i+1} ({loc_name})")
        
        dest_choice = input("  Choose location [1-3] > ").strip()
        try:
            dest_idx = int(dest_choice) - 1
            if dest_idx < 0 or dest_idx > 2:
                return ["Invalid location."]
        except ValueError:
            return ["Invalid input."]
        
        # Choose row
        row_choice = input("  Which row? [F]ront or [B]ack > ").strip().upper()
        target_row = "front" if row_choice.startswith("F") else "back"
        
        return self.game.move_ally(ally, player, dest_idx, target_row)
    
    def _handle_attack(self) -> list:
        """Handle declaring an attack."""
        msgs = []
        player = self.game.active_player
        board = self.game.board
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        
        # Find allies that can attack
        attack_options = []
        for loc_idx, loc in enumerate(board.locations):
            for ally in loc.get_allies(player):
                if ally.can_attack(player_state.turn_number):
                    targets = loc.valid_attack_targets(ally, player)
                    if targets:
                        attack_options.append((loc_idx, ally, targets))
        # Hero already included by loc.get_allies(player) above if at a location
        
        if not attack_options:
            return ["No allies can attack this turn! (Allies can't attack the turn they enter — wait for next turn when they untap.)"]
        
        print("\n  Choose attacker:")
        for j, (loc_idx, ally, targets) in enumerate(attack_options):
            print(f"    [{j+1}] {ally.card.name}({ally.card.power}/{ally.current_toughness}) at Loc {loc_idx+1} ({len(targets)} targets)")
        print("    [C] Cancel")
        
        choice = input("  Choose attacker > ").strip()
        if choice.upper() == "C":
            return ["Attack cancelled."]
        
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(attack_options):
                return ["Invalid choice."]
        except ValueError:
            return ["Invalid input."]
        
        loc_idx, attacker, targets = attack_options[idx]
        
        # Choose target
        print("\n  Choose target:")
        for j, (t_type, target) in enumerate(targets):
            if t_type == "location":
                loc = target
                print(f"    [{j+1}] Location: {loc.location_card.name} (Def {loc.current_defense})")
            else:
                print(f"    [{j+1}] {target.card.name}({target.card.power}/{target.current_toughness})")
        print("    [C] Cancel")
        
        t_choice = input("  Choose target > ").strip()
        if t_choice.upper() == "C":
            return ["Attack cancelled."]
        
        try:
            t_idx = int(t_choice) - 1
            if t_idx < 0 or t_idx >= len(targets):
                return ["Invalid choice."]
        except ValueError:
            return ["Invalid input."]
        
        t_type, target = targets[t_idx]
        
        # Resolve attack
        result = self.game.combat.resolve_attack(attacker, player, target, t_type)
        msgs.extend(result["messages"])
        
        # Check destruction aftermath
        if result.get("target_destroyed") and t_type in ("ally_front", "ally_back"):
            target_player = "shadow" if player == "fp" else "fp"
            # Remove destroyed ally from board
            board.remove_ally(target, target_player)
            # Discard
            enemy_state = self.game.shadow_player if player == "fp" else self.game.fp_player
            enemy_state.discard.append(target.card)
            # Death triggers
            death_msgs = self.game.effects.resolve_on_destroy(target, target_player)
            msgs.extend(death_msgs)
            
            # Check hero destruction
            if target is enemy_state.hero:
                enemy_state.hero = None
                enemy_state.hero_in_play = False
                enemy_state.leaderless = True
                msgs.append(f"{target.card.name} has fallen!")
                
                # Ring theft/recovery
                if target_player == "fp" and self.game.ring.bearer == "fp":
                    self.game.ring.steal_by_shadow()
                    msgs.append("*** The Ring has been seized by the Shadow! ***")
                elif target_player == "shadow" and self.game.ring.bearer == "shadow":
                    self.game.ring.recover_by_fp()
                    msgs.append("*** The Ring has been recovered by the Free Peoples! ***")
        
        # Check location flip aftermath
        if result.get("location_flipped"):
            msgs.append(f"Location flipped to {'Free Peoples' if board.get_location(loc_idx).controller == 'fp' else 'Shadow'} control!")
        
        # Check game over
        self.game._check_game_over()
        
        return msgs
