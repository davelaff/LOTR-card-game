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
from engine.events import resolve_event


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
        """Dispatch an event card to its handler in engine.events."""
        return resolve_event(self, card, player)
    
    
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
