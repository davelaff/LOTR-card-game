"""
Player state for the LOTR Card Battle Game.
"""

import random
from dataclasses import dataclass, field
from engine.card import Card, CardType, BoardAlly, Faction

@dataclass
class PlayerState:
    """Represents one player's entire game state."""
    name: str
    faction: Faction
    is_free_peoples: bool
    
    # Resources
    influence: int = 30
    willpower_max: int = 1  # Will be set per turn rules
    willpower_pool: int = 0
    
    # Cards
    deck: list = field(default_factory=list)
    hand: list = field(default_factory=list)
    discard: list = field(default_factory=list)
    
    # Hero
    hero: BoardAlly = None
    hero_in_play: bool = True
    
    # Leaderless penalty
    leaderless: bool = False
    
    # Fatigue tracking
    fatigue_counter: int = 0
    
    # Turn tracking
    turn_number: int = 0  # Which turn number this player is on
    
    def draw_card(self):
        """Draw a card from deck. Returns None if deck empty (fatigue)."""
        if not self.deck:
            self.fatigue_counter += 1
            self.influence -= self.fatigue_counter
            return None
        card = self.deck.pop()
        self.hand.append(card)
        return card
    
    def draw_cards(self, n: int) -> list:
        """Draw n cards."""
        drawn = []
        for _ in range(n):
            c = self.draw_card()
            if c:
                drawn.append(c)
        return drawn
    
    def shuffle_deck(self):
        """Shuffle the deck."""
        random.shuffle(self.deck)
    
    def play_card(self, card: Card) -> bool:
        """Remove a card from hand to play it. Returns True if found."""
        for i, c in enumerate(self.hand):
            if c.instance_id == card.instance_id:
                self.hand.pop(i)
                return True
        return False
    
    def discard_card(self, card: Card):
        """Discard a specific card from hand."""
        for i, c in enumerate(self.hand):
            if c is card or c.instance_id == card.instance_id:
                self.hand.pop(i)
                self.discard.append(c)
                return True
        return False
    
    def spend_willpower(self, amount: int) -> bool:
        """Try to spend willpower. Returns True if successful."""
        if self.willpower_pool >= amount:
            self.willpower_pool -= amount
            return True
        return False
    
    def add_willpower(self, amount: int):
        """Add temporary willpower (can exceed cap)."""
        self.willpower_pool += amount
    
    def deal_influence_damage(self, amount: int):
        """Deal direct damage to influence."""
        self.influence = max(0, self.influence - amount)
    
    def is_defeated(self) -> bool:
        """Check if this player has lost."""
        return self.influence <= 0
    
    @property
    def hand_size(self):
        return len(self.hand)
    
    @property
    def deck_size(self):
        return len(self.deck)
    
    @property
    def effective_willpower_max(self):
        """Willpower max after leaderless penalty."""
        if self.leaderless:
            return max(1, self.willpower_max - 2)
        return self.willpower_max

def create_starting_deck(faction: Faction, card_definitions: dict) -> list:
    """Create a starting deck for a given faction from card definitions."""
    from cards.gondor import GONDOR_DECK
    from cards.mordor import MORDOR_DECK
    from cards.elven import ELVEN_DECK
    from cards.dwarven import DWARVEN_DECK
    from cards.rohan import ROHAN_DECK
    from cards.hobbit import HOBBIT_DECK
    from cards.isengard import ISENGARD_DECK
    from cards.moria import MORIA_DECK
    from cards.harad import HARAD_DECK
    from cards.nazgul import NAZGUL_DECK
    
    deck_map = {
        Faction.GONDOR: GONDOR_DECK,
        Faction.MORDOR: MORDOR_DECK,
        Faction.ELVEN: ELVEN_DECK,
        Faction.DWARVEN: DWARVEN_DECK,
        Faction.ROHAN: ROHAN_DECK,
        Faction.HOBBIT: HOBBIT_DECK,
        Faction.ISENGARD: ISENGARD_DECK,
        Faction.MORIA: MORIA_DECK,
        Faction.HARAD: HARAD_DECK,
        Faction.NAZGUL: NAZGUL_DECK,
    }
    
    if faction in deck_map:
        return [c.clone() for c in deck_map[faction]]
    return []
