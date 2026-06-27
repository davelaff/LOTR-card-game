"""
Game state management and turn flow for the LOTR Card Battle Game.
"""

from typing import Optional
from engine.card import Card, CardType, BoardAlly, Keyword, Faction
from engine.player import PlayerState, create_starting_deck
from engine.board import Board, LocationSlot
from engine.ring import Ring
from engine.combat import CombatResolver
from engine.effects import EffectResolver


class GamePhase:
    START = "Start Phase"
    MAIN = "Main Phase"
    END = "End Phase"
    GAME_OVER = "Game Over"


def _create_hero(faction: Faction) -> Card:
    """Factory: create the hero card for a given faction."""
    if faction == Faction.GONDOR:
        from cards.gondor import create_gondor_hero
        return create_gondor_hero()
    elif faction == Faction.MORDOR:
        from cards.mordor import create_mordor_hero
        return create_mordor_hero()
    elif faction == Faction.ELVEN:
        from cards.elven import create_elven_hero
        return create_elven_hero()
    elif faction == Faction.DWARVEN:
        from cards.dwarven import create_dwarven_hero
        return create_dwarven_hero()
    elif faction == Faction.ROHAN:
        from cards.rohan import create_rohan_hero
        return create_rohan_hero()
    elif faction == Faction.HOBBIT:
        from cards.hobbit import create_hobbit_hero
        return create_hobbit_hero()
    elif faction == Faction.ISENGARD:
        from cards.isengard import create_isengard_hero
        return create_isengard_hero()
    elif faction == Faction.MORIA:
        from cards.moria import create_moria_hero
        return create_moria_hero()
    elif faction == Faction.HARAD:
        from cards.harad import create_harad_hero
        return create_harad_hero()
    elif faction == Faction.NAZGUL:
        from cards.nazgul import create_nazgul_hero
        return create_nazgul_hero()
    return None


def _is_shadow_faction(faction: Faction) -> bool:
    """Check if a faction belongs to Shadow."""
    return faction in (
        Faction.MORDOR, Faction.ISENGARD, Faction.MORIA,
        Faction.HARAD, Faction.NAZGUL,
    )


class GameState:
    """Top-level game state manager."""
    
    def __init__(self):
        self.fp_player: Optional[PlayerState] = None
        self.shadow_player: Optional[PlayerState] = None
        self.board: Board = Board()
        self.ring: Ring = Ring()
        self.combat: CombatResolver = CombatResolver(self)
        self.effects: EffectResolver = EffectResolver(self)
        
        self.current_phase: str = GamePhase.START
        self.active_player: str = "fp"  # Free Peoples always first
        self.current_turn_number: int = 1
        self.turn_count: int = 0  # Total turns elapsed
        
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.loss_reason: Optional[str] = None
        
        self.messages: list = []
        self.phase_messages: list = []
    
    def setup(self, fp_faction: Faction = Faction.GONDOR, 
              shadow_faction: Faction = Faction.MORDOR):
        """Initialize the game with chosen factions."""
        fp_name = f"Free Peoples ({fp_faction.value})"
        shadow_name = f"Shadow ({shadow_faction.value})"
        
        # Create players
        self.fp_player = PlayerState(
            name=fp_name,
            faction=fp_faction,
            is_free_peoples=True,
        )
        self.shadow_player = PlayerState(
            name=shadow_name,
            faction=shadow_faction,
            is_free_peoples=False,
        )
        
        # Create and place Heroes
        fp_hero_card = _create_hero(fp_faction)
        shadow_hero_card = _create_hero(shadow_faction)
        
        if fp_hero_card:
            self.fp_player.hero = BoardAlly(
                card=fp_hero_card,
                current_toughness=fp_hero_card.toughness,
                turn_entered=0,
            )
            self.board.deploy_ally(self.fp_player.hero, "fp")
        
        if shadow_hero_card:
            self.shadow_player.hero = BoardAlly(
                card=shadow_hero_card,
                current_toughness=shadow_hero_card.toughness,
                turn_entered=0,
            )
            self.board.deploy_ally(self.shadow_player.hero, "shadow")
        
        # Create and shuffle decks
        self.fp_player.deck = create_starting_deck(fp_faction, {})
        self.shadow_player.deck = create_starting_deck(shadow_faction, {})
        self.fp_player.shuffle_deck()
        self.shadow_player.shuffle_deck()
        
        # Draw opening hands (5 cards each)
        self.fp_player.draw_cards(5)
        self.shadow_player.draw_cards(5)
        
        # Set initial willpower
        self.fp_player.willpower_max = 0
        self.shadow_player.willpower_max = 0
        
        self.messages.append("Game setup complete!")
        self.messages.append(f"{fp_name} vs {shadow_name}")
        self.messages.append("Opening hands drawn (5 cards each).")
    
    def start_turn(self):
        """Execute the Start Phase."""
        self.current_phase = GamePhase.START
        active = self.fp_player if self.active_player == "fp" else self.shadow_player
        active.turn_number += 1
        
        self.phase_messages = []
        self.phase_messages.append(f"--- {active.name}'s Turn {active.turn_number} ---")
        self.phase_messages.append(f"Phase: {GamePhase.START}")
        
        # Clean up dead allies from board (locations + deployment)
        for loc in self.board.locations:
            for player_id in ("fp", "shadow"):
                for row in (loc.get_front_line(player_id), loc.get_back_line(player_id)):
                    for ally in list(row):
                        if not ally.is_alive:
                            row.remove(ally)
                            state = self.fp_player if player_id == "fp" else self.shadow_player
                            state.discard.append(ally.card)
        # Also clean deployment zones
        for player_id in ("fp", "shadow"):
            zone = self.board.fp_deployment if player_id == "fp" else self.board.shadow_deployment
            state = self.fp_player if player_id == "fp" else self.shadow_player
            for ally in list(zone):
                if not ally.is_alive:
                    zone.remove(ally)
                    state.discard.append(ally.card)
        
        # Untap all allies at locations
        untapped = 0
        for loc in self.board.locations:
            for ally in loc.get_allies(self.active_player):
                ally.tapped = False
                ally.has_attacked_this_turn = False
                ally.has_moved_this_turn = False
                untapped += 1
        # Untap allies in deployment zone
        zone = self.board.fp_deployment if self.active_player == "fp" else self.board.shadow_deployment
        for ally in zone:
            ally.tapped = False
            ally.has_attacked_this_turn = False
            ally.has_moved_this_turn = False
            untapped += 1
        # Untap hero
        hero = active.hero
        if hero and hero.is_alive:
            hero.tapped = False
            hero.has_attacked_this_turn = False
            hero.has_moved_this_turn = False
            hero.has_used_ability_this_turn = False
        
        self.phase_messages.append(f"Untapped {untapped} allies + Hero.")
        
        # Willpower step
        if active.turn_number == 1:
            active.willpower_max = 1  # Both players start with 1 WP on turn 1
        else:
            if active.willpower_max < 10:
                active.willpower_max += 1
        
        active.willpower_pool = active.effective_willpower_max
        self.phase_messages.append(
            f"Willpower: {active.willpower_pool}/{active.effective_willpower_max}"
        )
        
        # Draw step — active player draws 1 card
        drawn = active.draw_card()
        if drawn:
            self.phase_messages.append(f"Drew {drawn.display_name}.")
        
        # Ring start-of-turn
        self.ring.start_turn()
        
        # Corruption check
        corr_status = self.ring.get_corruption_status()
        self.phase_messages.append(f"Ring: {corr_status}")
        
        # Progress to Main Phase
        self.current_phase = GamePhase.MAIN
        self.phase_messages.append(f"Phase: {GamePhase.MAIN}")
    
    def end_turn(self):
        """Execute the End Phase."""
        self.current_phase = GamePhase.END
        active = self.fp_player if self.active_player == "fp" else self.shadow_player
        
        self.phase_messages = []
        self.phase_messages.append(f"--- {GamePhase.END} for {active.name} ---")
        
        # Ring end-of-turn
        self.ring.end_turn(self.active_player)
        
        # Clear temporary effects from all allies
        for loc in self.board.locations:
            for player_id in ("fp", "shadow"):
                for ally in loc.get_allies(player_id):
                    ally.clear_temp_bonuses()
        for player_id in ("fp", "shadow"):
            zone = self.board.fp_deployment if player_id == "fp" else self.board.shadow_deployment
            for ally in zone:
                ally.clear_temp_bonuses()
        # Also clear hero temp bonuses
        if self.fp_player.hero:
            self.fp_player.hero.clear_temp_bonuses()
        if self.shadow_player.hero:
            self.shadow_player.hero.clear_temp_bonuses()
        
        self.phase_messages.append("Temporary effects expire.")
        
        # Switch active player
        self.active_player = "shadow" if self.active_player == "fp" else "fp"
        self.current_turn_number += 1
        
        # Check game over conditions
        self._check_game_over()
        
        if not self.game_over:
            self.phase_messages.append(
                f"Turn passes to "
                f"{'Free Peoples' if self.active_player == 'fp' else 'Shadow'}."
            )
    
    def _check_game_over(self) -> Optional[str]:
        """Check all loss conditions. Returns winner or None."""
        # Influence check
        if self.fp_player.is_defeated():
            self.game_over = True
            self.winner = "shadow"
            self.loss_reason = "Free Peoples' Influence reduced to 0!"
            self.current_phase = GamePhase.GAME_OVER
            self.phase_messages.append(f"GAME OVER: {self.loss_reason}")
            return "shadow"
        
        if self.shadow_player.is_defeated():
            self.game_over = True
            self.winner = "fp"
            self.loss_reason = "Shadow's Influence reduced to 0!"
            self.current_phase = GamePhase.GAME_OVER
            self.phase_messages.append(f"GAME OVER: {self.loss_reason}")
            return "fp"
        
        # Corruption check
        loser = self.ring.check_corruption_loss()
        if loser:
            self.game_over = True
            self.winner = "shadow" if loser == "fp" else "fp"
            self.loss_reason = f"Corruption reached 30! {'Free Peoples' if loser == 'fp' else 'Shadow'} loses!"
            self.current_phase = GamePhase.GAME_OVER
            self.phase_messages.append(f"GAME OVER: {self.loss_reason}")
            return self.winner
        
        # Deck exhaustion double-check
        if self.fp_player.influence <= 0:
            self.game_over = True
            self.winner = "shadow"
            self.loss_reason = "Free Peoples' Influence reduced to 0 (fatigue)!"
            self.current_phase = GamePhase.GAME_OVER
            return "shadow"
        
        if self.shadow_player.influence <= 0:
            self.game_over = True
            self.winner = "fp"
            self.loss_reason = "Shadow's Influence reduced to 0 (fatigue)!"
            self.current_phase = GamePhase.GAME_OVER
            return "fp"
        
        return None
    
    def play_card(self, card: Card, player: str) -> list:
        """Play a card from hand. Returns list of messages."""
        msgs = []
        player_state = self.fp_player if player == "fp" else self.shadow_player
        
        # Check willpower
        if not player_state.spend_willpower(card.cost):
            msgs.append(f"Not enough Willpower! Need {card.cost}, have {player_state.willpower_pool}.")
            return msgs
        
        # Remove from hand
        if not player_state.play_card(card):
            msgs.append("Card not in hand!")
            return msgs
        
        msgs.append(f"Played {card.display_name} for {card.cost} WP.")
        
        if card.card_type == CardType.ALLY:
            # Create board ally
            ally = BoardAlly(
                card=card,
                current_toughness=card.toughness,
                turn_entered=player_state.turn_number,
                tapped=True,  # Summoning sickness
            )
            if Keyword.CHARGE in card.keywords:
                ally.tapped = False
            
            # Deploy to deployment zone
            self.board.deploy_ally(ally, player)
            msgs.append(f"{card.name} enters deployment zone.")
            
            # Check Ambush
            if Keyword.AMBUSH in card.keywords:
                msgs.append("Ambush: can deploy directly to contested location (auto for AI).")
            
            # Trigger on-enter effects
            enter_msgs = self.effects.resolve_on_enter(ally, player)
            msgs.extend(enter_msgs)
        
        elif card.card_type == CardType.EVENT:
            # Events resolve and go to discard
            msgs.extend(self._resolve_event(card, player))
            player_state.discard.append(card)
        
        elif card.card_type == CardType.ARTIFACT:
            hero = player_state.hero
            if hero:
                hero.artifacts.append(card)
                msgs.append(f"{card.name} attached to {hero.card.name}.")
            else:
                msgs.append("No hero to attach artifact to!")
                player_state.discard.append(card)
        
        elif card.card_type == CardType.LOCATION:
            placed = False
            for i, loc in enumerate(self.board.locations):
                if loc.is_empty():
                    self.board.play_location(card, player, i)
                    msgs.append(f"{card.name} placed at Location Slot {i+1} (Def {card.defense}).")
                    placed = True
                    break
            if not placed:
                msgs.append("No empty location slots available!")
                player_state.discard.append(card)
        
        return msgs
    
    def _resolve_event(self, card: Card, player: str) -> list:
        """Resolve an event card's effect."""
        msgs = []
        enemy = "shadow" if player == "fp" else "fp"
        player_state = self.fp_player if player == "fp" else self.shadow_player
        enemy_state = self.shadow_player if player == "fp" else self.fp_player
        
        faction = card.faction
        
        # --- Gondor events ---
        if card.name == "The Beacons Are Lit":
            found = None
            deck = player_state.deck
            search_count = min(5, len(deck))
            searched = []
            for _ in range(search_count):
                c = deck.pop()
                if c.card_type == CardType.ALLY and c.faction == Faction.GONDOR and not found:
                    found = c
                else:
                    searched.append(c)
            if found:
                player_state.hand.append(found)
                msgs.append(f"Found {found.name}! Added to hand.")
            deck.extend(searched)
            player_state.shuffle_deck()
            msgs.append(f"Searched {search_count} cards.")
        
        elif card.name == "For Gondor!":
            count = 0
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    ally.toughness_bonus += 2
                    count += 1
            msgs.append(f"For Gondor! {count} allies gain +2 Toughness this turn.")
        
        elif card.name == "The Last Debate":
            search_count = min(7, len(player_state.deck))
            msgs.append(f"Looked at top {search_count} cards. (Simplified: draw 1)")
            player_state.draw_card()
        
        # --- Mordor events ---
        elif card.name == "The Shadow Spreads":
            self.ring.add_corruption(1)
            msgs.append(f"Shadow Spreads: +1 Corruption (now {self.ring.corruption}/30).")
            for loc in self.board.locations:
                if loc.controller == player or loc.is_contested():
                    from engine.effects import create_orc_token
                    token = create_orc_token()
                    token_ally = BoardAlly(
                        card=token, current_toughness=token.toughness,
                        turn_entered=player_state.turn_number,
                    )
                    loc.add_ally(token_ally, player, "front")
                    msgs.append(f"Created Orc Token at {loc.location_card.name if loc.location_card else 'Open Field'}.")
                    break
        
        elif card.name == "Shadow's Reach":
            enemy_state.deal_influence_damage(2)
            self.ring.add_corruption(1)
            msgs.append(f"Shadow's Reach: 2 Burn damage to {'Free Peoples' if enemy == 'fp' else 'Shadow'} Influence!")
            msgs.append(f"+1 Corruption (now {self.ring.corruption}/30).")
        
        elif card.name == "The Lidless Eye":
            self.ring.add_corruption(1)
            msgs.append(f"Lidless Eye: +1 Corruption (now {self.ring.corruption}/30).")
            if enemy_state.hand:
                discarded = enemy_state.hand.pop()
                enemy_state.discard.append(discarded)
                msgs.append(f"Opponent discards {discarded.name}.")
        
        elif card.name == "The Fires of Mount Doom":
            self.ring.add_corruption(2)
            for loc in self.board.locations:
                for ally in loc.get_allies(enemy):
                    ally.take_damage(3)
            msgs.append("Fires of Mount Doom: 3 damage to all enemies! +2 Corruption.")
        
        # --- Elven events ---
        elif card.name == "Lembas":
            # Heal 3 from a wounded ally (simplified: heal hero)
            hero = player_state.hero
            if hero and hero.damage > 0:
                healed = hero.heal(3)
                msgs.append(f"Lembas: Healed {healed} damage from {hero.card.name} (+1 Power this turn).")
            else:
                msgs.append("Lembas: No damage to heal. (+1 Power still gained.)")
        
        elif card.name == "The Last Alliance":
            count = min(8, len(player_state.deck))
            msgs.append(f"The Last Alliance: Revealed top {count}. (Simplified: draw 2)")
            player_state.draw_cards(2)
        
        elif card.name == "The Light of the Evenstar":
            # Target gains Stealth and +1/+1. Heal 1 at end of turn.
            # Auto-target: own hero or strongest ally
            target = None
            hero = player_state.hero
            if hero and hero.is_alive:
                target = hero
            else:
                all_allies = self.board.get_all_allies(player)
                if all_allies:
                    target = max(all_allies, key=lambda a: a.card.power)
            if target:
                target.add_temp_keyword(Keyword.STEALTH)
                target.power_bonus += 1
                target.toughness_bonus += 1
                msgs.append(f"Light of the Evenstar: {target.card.name} gains Stealth and +1/+1 this turn.")
            else:
                msgs.append("Light of the Evenstar: No valid target.")
        
        # --- Dwarven events ---
        elif card.name == "To Me! O My Kinsfolk!":
            count = min(5, len(player_state.deck))
            msgs.append(f"To Me! O My Kinsfolk!: Revealed top {count}. (Simplified: draw 1)")
            player_state.draw_card()
        
        elif card.name == "The Ire of the Mountain":
            # Destroy target Artifact or Location. Draw 2 if you control a Dwarf.
            destroyed = False
            # Priority: enemy artifact first, then enemy location
            for loc in self.board.locations:
                if loc.controller == enemy and loc.location_card and loc.current_defense > 0:
                    # Destroy the location
                    loc_name = loc.location_card.name
                    loc.location_card = None
                    loc.current_defense = 0
                    loc.controller = None
                    loc.fortify_bonus = 0
                    msgs.append(f"The Ire of the Mountain: Destroyed {loc_name}!")
                    destroyed = True
                    break
                # Check for enemy artifacts at this location
                for ally in loc.get_allies(enemy):
                    if ally.artifacts:
                        art = ally.artifacts.pop(0)
                        enemy_state.discard.append(art)
                        msgs.append(f"The Ire of the Mountain: Destroyed {art.name}!")
                        destroyed = True
                        break
                if destroyed:
                    break
            if not destroyed:
                msgs.append("The Ire of the Mountain: No enemy Artifact or Location to destroy.")
            # Draw 2 if you control a Dwarf
            has_dwarf = False
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if "Dwarf" in ally.card.creature_types:
                        has_dwarf = True
                        break
            if has_dwarf:
                drawn = player_state.draw_cards(2)
                msgs.append(f"Controlling a Dwarf: Drew {len(drawn)} cards.")
        
        elif card.name == "The Hammer Falls":
            # Deal 4 damage to allies at a single location (center/busiest)
            target_loc = self.board.get_location(1)  # Center location
            for ally in target_loc.get_allies(enemy):
                ally.take_damage(4)
            msgs.append("The Hammer Falls: 4 damage to enemies at center location!")
        
        # --- Rohan events ---
        elif card.name == "Ride of the Rohirrim":
            # Target Rohan ally gains Charge and +2 Power. If already Charge, +3 instead.
            # Auto-target: strongest Rohan ally (including hero) at any location
            target = None
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if ally.card.faction == Faction.ROHAN or "Rider" in ally.card.creature_types:
                        if target is None or ally.card.power > target.card.power:
                            target = ally
            if player_state.hero and player_state.hero.card.faction == Faction.ROHAN:
                h = player_state.hero
                if h.is_alive and (target is None or h.card.power > target.card.power):
                    target = h
            if target:
                already_charge = target.has_charge
                target.add_temp_keyword(Keyword.CHARGE)
                bonus = 3 if already_charge else 2
                target.power_bonus += bonus
                msgs.append(f"Ride of the Rohirrim: {target.card.name} gains Charge and +{bonus} Power!")
            else:
                msgs.append("Ride of the Rohirrim: No Rohan ally to target.")
        
        elif card.name == "Muster the Rohirrim":
            # Create three 2/1 Rider tokens with Charge. Deploy to any locations you control.
            from engine.effects import create_rider_token
            deployed = 0
            controlled_locs = [loc for loc in self.board.locations 
                             if loc.controller == player and not loc.is_empty()]
            for i in range(3):
                rider_card = create_rider_token()
                rider = BoardAlly(
                    card=rider_card,
                    current_toughness=rider_card.toughness,
                    turn_entered=player_state.turn_number,
                    tapped=False,  # Charge
                )
                if controlled_locs:
                    # Distribute evenly across controlled locations
                    target_loc = controlled_locs[i % len(controlled_locs)]
                    target_loc.add_ally(rider, player, "front")
                    deployed += 1
                else:
                    # Fallback to deployment zone
                    self.board.deploy_ally(rider, player)
            msgs.append(f"Muster the Rohirrim: Created 3 Rider tokens (2/1 Charge)! {deployed} deployed to locations.")
        
        elif card.name == "Forth Eorlingas!":
            # Up to 3 Rohan allies gain Charge and +2 Power. They take 1 damage after turn.
            rohan_allies = []
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if ally.card.faction == Faction.ROHAN or "Rider" in ally.card.creature_types:
                        rohan_allies.append(ally)
            # Pick strongest (up to 3)
            rohan_allies.sort(key=lambda a: a.card.power, reverse=True)
            buffed = rohan_allies[:3]
            for ally in buffed:
                ally.add_temp_keyword(Keyword.CHARGE)
                ally.power_bonus += 2
                ally.take_damage(1)  # They take 1 damage (applied immediately as simplification)
            msgs.append(f"Forth Eorlingas! {len(buffed)} Rohan allies gain Charge and +2 Power (take 1 damage)!")
        
        # --- Hobbit events ---
        elif card.name == "The Straight Road":
            msgs.append("The Straight Road: Ally gains Stealth. Draw a card if it survives.")
            player_state.draw_card()
        
        elif card.name == "I Will Not Say the Day Is Done":
            removed = min(3, self.ring.corruption)
            for _ in range(removed):
                if self.ring.corruption > 0:
                    self.ring.corruption -= 1
            drawn = player_state.draw_cards(removed)
            msgs.append(f"I Will Not Say: Removed {removed} Corruption! Drew {len(drawn)} cards.")
        
        # --- Isengard events ---
        elif card.name == "The White Hand":
            # Target Uruk-hai gains +2/+2. If at contested, destroy enemy Artifact there.
            target = None
            target_loc = None
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if "Uruk-hai" in ally.card.creature_types:
                        if target is None or ally.card.power > target.card.power:
                            target = ally
                            target_loc = loc
            if target:
                target.power_bonus += 2
                target.toughness_bonus += 2
                msgs.append(f"The White Hand: {target.card.name} gains +2/+2!")
                # If at contested, destroy enemy artifact
                if target_loc and target_loc.is_contested():
                    art_destroyed = False
                    for enemy_ally in target_loc.get_allies(enemy):
                        if enemy_ally.artifacts:
                            art = enemy_ally.artifacts.pop(0)
                            enemy_state.discard.append(art)
                            msgs.append(f"The White Hand: Destroyed {art.name} at contested location!")
                            art_destroyed = True
                            break
                    if not art_destroyed:
                        msgs.append("The White Hand: Contested, but no enemy Artifact to destroy.")
            else:
                msgs.append("The White Hand: No Uruk-hai ally to target.")
        
        elif card.name == "Isengard Unleashed":
            # Reveal top 6, put Uruk-hai allies into play with Charge.
            reveal_count = min(6, len(player_state.deck))
            put_in_play = []
            rest = []
            for _ in range(reveal_count):
                c = player_state.deck.pop()
                if (c.card_type == CardType.ALLY and 
                    "Uruk-hai" in c.creature_types):
                    put_in_play.append(c)
                else:
                    rest.append(c)
            # Put Uruk-hai into play
            for c in put_in_play:
                ally = BoardAlly(
                    card=c,
                    current_toughness=c.toughness,
                    turn_entered=player_state.turn_number,
                    tapped=False,  # Charge
                )
                # Deploy to location
                target_loc_idx = -1
                for i, loc in enumerate(self.board.locations):
                    if loc.controller == player or loc.is_contested():
                        target_loc_idx = i
                        break
                if target_loc_idx >= 0:
                    self.board.get_location(target_loc_idx).add_ally(ally, player, "front")
                else:
                    self.board.deploy_ally(ally, player)
            # Return rest to bottom
            player_state.deck = rest + player_state.deck
            msgs.append(f"Isengard Unleashed: Revealed {reveal_count}, put {len(put_in_play)} Uruk-hai into play with Charge!")
        
        elif card.name == "A New Power Rises":
            # Destroy all Artifacts at location. Create 3/3 Uruk-hai tokens for each.
            from engine.effects import create_uruk_hai_token
            # Pick busiest or contested location
            target_loc = None
            best_score = -1
            for loc in self.board.locations:
                score = len(loc.get_allies(player)) + len(loc.get_allies(enemy))
                if score > best_score:
                    best_score = score
                    target_loc = loc
            if target_loc is None:
                target_loc = self.board.get_location(1)  # Center fallback
            # Count and destroy artifacts
            artifacts_destroyed = 0
            for row_name in ["fp_front", "fp_back", "shadow_front", "shadow_back"]:
                row = getattr(target_loc, row_name, [])
                for ally in row:
                    while ally.artifacts:
                        art = ally.artifacts.pop()
                        artifacts_destroyed += 1
                        # Figure out owner
                        if row_name.startswith("fp"):
                            self.fp_player.discard.append(art)
                        else:
                            self.shadow_player.discard.append(art)
            # Create tokens
            for _ in range(artifacts_destroyed):
                token_card = create_uruk_hai_token()
                token = BoardAlly(
                    card=token_card,
                    current_toughness=token_card.toughness,
                    turn_entered=player_state.turn_number,
                )
                target_loc.add_ally(token, player, "front")
            msgs.append(f"A New Power Rises: Destroyed {artifacts_destroyed} artifacts, created {artifacts_destroyed} 3/3 Uruk-hai tokens!")
        
        # --- Moria events ---
        elif card.name == "Drums in the Deep":
            # Return up to 2 Goblins from discard to hand. Create 1/1 Goblin token.
            returned = 0
            grab = []
            for c in list(player_state.discard):
                if "Goblin" in c.creature_types and returned < 2:
                    grab.append(c)
                    returned += 1
            for c in grab:
                player_state.discard.remove(c)
                player_state.hand.append(c)
            # Create 1/1 Goblin token at a controlled/contested location
            from engine.effects import create_goblin_token
            token_card = create_goblin_token()
            token = BoardAlly(
                card=token_card,
                current_toughness=token_card.toughness,
                turn_entered=player_state.turn_number,
            )
            placed = False
            for loc in self.board.locations:
                if loc.controller == player or loc.is_contested():
                    loc.add_ally(token, player, "front")
                    placed = True
                    break
            if not placed:
                self.board.deploy_ally(token, player)
            msgs.append(f"Drums in the Deep: Returned {returned} Goblins from discard + created Goblin token!")
        
        elif card.name == "They Are Coming":
            # Put up to 3 Goblins from hand into location via Ambush. They gain Charge.
            goblins = []
            for c in list(player_state.hand):
                if "Goblin" in c.creature_types and len(goblins) < 3:
                    goblins.append(c)
            # Remove from hand and deploy
            for c in goblins:
                player_state.hand.remove(c)
                ally = BoardAlly(
                    card=c,
                    current_toughness=c.toughness,
                    turn_entered=player_state.turn_number,
                    tapped=False,  # Ambush + Charge
                )
                # Find contested or enemy-controlled location (Ambush)
                placed = False
                for loc in self.board.locations:
                    if loc.is_contested() or loc.controller == enemy:
                        loc.add_ally(ally, player, "front")
                        placed = True
                        break
                if not placed:
                    # Fallback: player's own location or deployment
                    for loc in self.board.locations:
                        if loc.controller == player:
                            loc.add_ally(ally, player, "front")
                            placed = True
                            break
                if not placed:
                    self.board.deploy_ally(ally, player)
            msgs.append(f"They Are Coming: {len(goblins)} Goblins deployed via Ambush with Charge!")
        
        elif card.name == "The Chasm Opens":
            # Deal 2 damage to enemies at busiest location
            busiest = max(self.board.locations, key=lambda l: len(l.get_allies(enemy)))
            for ally in busiest.get_allies(enemy):
                ally.take_damage(2)
            msgs.append("The Chasm Opens: All Goblins relocated! 2 damage at busiest location!")
        
        # --- Harad events ---
        elif card.name == "The Serpent's Coil":
            # Target Haradrim gains Intimidate. If Mumak, gains it permanently.
            target = None
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if (ally.card.faction == Faction.HARAD or 
                        any(t in ally.card.creature_types for t in ["Haradrim", "Easterling", "Mumak"])):
                        if target is None or ally.card.power > target.card.power:
                            target = ally
            if target:
                is_mumak = "Mumak" in target.card.creature_types
                if is_mumak:
                    if Keyword.INTIMIDATE not in target.card.keywords:
                        target.card.keywords.append(Keyword.INTIMIDATE)
                    msgs.append(f"The Serpent's Coil: {target.card.name} gains Intimidate permanently!")
                else:
                    target.add_temp_keyword(Keyword.INTIMIDATE)
                    msgs.append(f"The Serpent's Coil: {target.card.name} gains Intimidate this turn.")
            else:
                msgs.append("The Serpent's Coil: No Haradrim ally to target.")
        
        elif card.name == "From the South and East":
            # Search top 6 for a Harad ally, put into play with Charge.
            search_count = min(6, len(player_state.deck))
            found = None
            rest = []
            for _ in range(search_count):
                c = player_state.deck.pop()
                if (not found and c.card_type == CardType.ALLY and 
                    c.faction == Faction.HARAD):
                    found = c
                else:
                    rest.append(c)
            player_state.deck = rest + player_state.deck
            if found:
                ally = BoardAlly(
                    card=found,
                    current_toughness=found.toughness,
                    turn_entered=player_state.turn_number,
                    tapped=False,  # Charge
                )
                for loc in self.board.locations:
                    if loc.controller == player or loc.is_contested():
                        loc.add_ally(ally, player, "front")
                        break
                else:
                    self.board.deploy_ally(ally, player)
                msgs.append(f"From the South and East: Found {found.name}, deployed with Charge!")
            else:
                msgs.append(f"From the South and East: No Harad ally in top {search_count}.")
        
        elif card.name == "The War-beasts Rampage":
            # Target Mumak gains +2 Power and attacks twice. Deals Power as Influence damage.
            target = None
            target_loc = None
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if "Mumak" in ally.card.creature_types:
                        target = ally
                        target_loc = loc
                        break
            if target:
                target.power_bonus += 2
                msgs.append(f"The War-beasts Rampage: {target.card.name} gains +2 Power!")
                # Attack twice at the location
                enemy_allies = target_loc.get_allies(enemy) if target_loc else []
                attacks = min(2, len(enemy_allies))
                for i in range(attacks):
                    if i < len(enemy_allies):
                        e = enemy_allies[i]
                        if e.is_alive:
                            dmg = target.effective_power
                            e.take_damage(dmg)
                            msgs.append(f"  Mumak attacks {e.card.name} for {dmg} damage!")
                            # Influence damage on excess (Trample-like)
                            if dmg > e.current_toughness + e.damage:
                                excess = dmg - (e.current_toughness + e.damage)
                                if excess > 0:
                                    enemy_state.deal_influence_damage(excess)
                                    msgs.append(f"  Rampage: {excess} excess damage to enemy Influence!")
                if attacks == 0 and target_loc:
                    # No enemy allies, attack location or influence directly
                    enemy_state.deal_influence_damage(target.effective_power)
                    msgs.append(f"  Mumak rampages! {target.effective_power} damage to enemy Influence!")
            else:
                msgs.append("The War-beasts Rampage: No Mumak to target.")
        
        # --- Nazgul events ---
        elif card.name == "All Shall Fade":
            # Target gains Wraith Form. If Nazgul, deal 3 damage to enemy at same location.
            # Auto-target: strongest Nazgul ally, or any ally if no Nazgul
            target = None
            target_loc = None
            for loc in self.board.locations:
                for ally in loc.get_allies(player):
                    if ally.card.faction == Faction.NAZGUL or "Nazgul" in ally.card.creature_types:
                        if target is None or ally.card.power > target.card.power:
                            target = ally
                            target_loc = loc
            # Fallback: any ally
            if target is None:
                for loc in self.board.locations:
                    for ally in loc.get_allies(player):
                        if target is None or ally.card.power > target.card.power:
                            target = ally
                            target_loc = loc
            if target:
                if Keyword.WRATH_FORM not in target.card.keywords:
                    target.card.keywords.append(Keyword.WRATH_FORM)
                msgs.append(f"All Shall Fade: {target.card.name} gains Wraith Form!")
                # If it's a Nazgul, deal 3 damage to enemy at same location
                is_nazgul = (target.card.faction == Faction.NAZGUL or 
                            "Nazgul" in target.card.creature_types)
                if is_nazgul and target_loc:
                    for enemy_ally in target_loc.get_allies(enemy):
                        enemy_ally.take_damage(3)
                    msgs.append(f"All Shall Fade: 3 damage to enemies at location!")
            else:
                msgs.append("All Shall Fade: No valid target.")
        
        elif card.name == "The Ring Is Mine":
            self.ring.add_corruption(1)
            msgs.append(f"The Ring Is Mine: +1 Corruption (now {self.ring.corruption}/30). FP may activate Ring or lose 3 Influence.")
            # Simplified: deal 3 influence damage
            enemy_state.deal_influence_damage(3)
            msgs.append("Free Peoples lose 3 Influence from the Ring's call!")
        
        else:
            msgs.append(f"{card.name} resolved (generic event).")
        
        return msgs
    
    def move_ally(self, ally: BoardAlly, player: str, 
                  target_location: int, target_row: str = "front") -> list:
        """Move an ally. Returns messages."""
        msgs = []
        current_loc = self.board.find_ally_location(ally, player)
        
        if current_loc is None:
            msgs.append("Ally not found on board!")
            return msgs
        
        if not ally.can_move() and not (current_loc == -1):
            msgs.append(f"{ally.card.name} cannot move (tapped or already acted)!")
            return msgs
        
        if current_loc == -1:
            # From deployment to location
            if self.board.move_ally_to_location(ally, player, target_location, target_row):
                msgs.append(f"{ally.card.name} moves to Location {target_location+1} ({target_row}).")
            else:
                msgs.append("Move failed — row may be full.")
        elif current_loc == target_location:
            # Row swap
            if self.board.move_ally_between_rows(ally, player, target_location, target_row):
                msgs.append(f"{ally.card.name} moves to {target_row} line at Location {target_location+1}.")
            else:
                msgs.append("Already in that row or move failed.")
        else:
            # Between locations
            if self.board.move_ally_between_locations(ally, player, current_loc, target_location, target_row):
                msgs.append(f"{ally.card.name} moves from Location {current_loc+1} to {target_location+1}.")
            else:
                msgs.append("Move failed — row may be full or not adjacent.")
        
        # Movement costs the ally's action
        ally.tapped = True
        ally.has_moved_this_turn = True
        
        return msgs
    
    def get_player_state(self, player: str) -> PlayerState:
        return self.fp_player if player == "fp" else self.shadow_player
    
    def get_enemy_state(self, player: str) -> PlayerState:
        return self.shadow_player if player == "fp" else self.fp_player
