"""
Card data model for the LOTR Card Battle Game.
Defines card types, keywords, and the Card class structure.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable, Any

class CardType(Enum):
    HERO = "Hero"
    ALLY = "Ally"
    EVENT = "Event"
    ARTIFACT = "Artifact"
    LOCATION = "Location"

class Faction(Enum):
    GONDOR = "Gondor"
    MORDOR = "Mordor"
    ELVEN = "Elven"
    DWARVEN = "Dwarven"
    ROHAN = "Rohan"
    HOBBIT = "Hobbit"
    ISENGARD = "Isengard"
    MORIA = "Moria"
    HARAD = "Harad"
    NAZGUL = "Nazgul"
    NEUTRAL = "Neutral"

class Keyword(Enum):
    CHARGE = "Charge"
    RANGED = "Ranged"
    STEALTH = "Stealth"
    TRAMPLE = "Trample"
    FEAR = "Fear"
    FORTIFY = "Fortify"
    RALLY = "Rally"
    SWARM = "Swarm"
    BURN = "Burn"
    SUNDER = "Sunder"
    SENTINEL = "Sentinel"
    STEADFAST = "Steadfast"
    VALOUR = "Valour"
    BRUTAL = "Brutal"
    AMBUSH = "Ambush"
    SCOUT = "Scout"
    SACRIFICE = "Sacrifice"
    INTIMIDATE = "Intimidate"
    DARKNESS = "Darkness"
    TUNNEL = "Tunnel"
    GRUDGE = "Grudge"
    FORESIGHT = "Foresight"
    GRACE = "Grace"
    DELVE = "Delve"
    RESILIENCE = "Resilience"
    MUSTER = "Muster"
    DEATH_CRY = "DeathCry"
    WRATH_FORM = "WraithForm"
    TERRIFY = "Terrify"
    DOMINATE = "Dominate"
    INDUSTRY = "Industry"
    SIEGE = "Siege"
    FORMATION = "Formation"
    STAMPEDE = "Stampede"
    SKYBORNE = "Skyborne"
    FELLOWSHIP = "Fellowship"
    CARRY = "Carry"
    RAMP = "Ramp"
    OATHBREAKER = "Oathbreaker"

@dataclass
class Card:
    """Represents a card in the game."""
    name: str
    faction: Faction
    card_type: CardType
    cost: int  # Willpower cost (0 for Heroes)
    power: int = 0
    toughness: int = 0
    defense: int = 0  # For locations
    rarity: str = "Common"
    rules_text: str = ""
    flavor_text: str = ""
    creature_types: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    
    # Unique ID for tracking
    instance_id: int = 0
    
    def __post_init__(self):
        if self.instance_id == 0:
            import random
            self.instance_id = random.randint(1, 999999)
    
    @property
    def is_creature(self):
        return self.card_type in (CardType.HERO, CardType.ALLY)
    
    @property
    def display_name(self):
        """Rich display name with stats."""
        if self.card_type == CardType.HERO:
            return f"{self.name}({self.power}/{self.toughness})"
        elif self.card_type == CardType.ALLY:
            return f"{self.name}({self.power}/{self.toughness})"
        elif self.card_type == CardType.LOCATION:
            return f"{self.name}(Def {self.defense})"
        elif self.card_type == CardType.ARTIFACT:
            return f"{self.name}[Art]"
        elif self.card_type == CardType.EVENT:
            return f"{self.name}[Evt]"
        return self.name
    
    def clone(self):
        """Create a fresh copy of this card for deck shuffling."""
        import random
        c = Card(
            name=self.name,
            faction=self.faction,
            card_type=self.card_type,
            cost=self.cost,
            power=self.power,
            toughness=self.toughness,
            defense=self.defense,
            rarity=self.rarity,
            rules_text=self.rules_text,
            flavor_text=self.flavor_text,
            creature_types=list(self.creature_types),
            keywords=list(self.keywords),
            instance_id=random.randint(1, 999999),
        )
        return c

# Card-on-board wrapper
@dataclass
class BoardAlly:
    """Represents an ally or hero on the battlefield."""
    card: Card
    current_toughness: int
    damage: int = 0
    tapped: bool = False
    artifacts: list = field(default_factory=list)
    turn_entered: int = 0
    has_attacked_this_turn: bool = False
    has_moved_this_turn: bool = False
    has_used_ability_this_turn: bool = False
    
    # Temporary modifiers (for event effects, hero abilities, etc.)
    power_bonus: int = 0
    toughness_bonus: int = 0
    temporary_keywords: set = field(default_factory=set)
    
    @property
    def effective_power(self):
        return self.card.power + self.power_bonus
    
    @property
    def effective_toughness(self):
        return self.current_toughness + self.toughness_bonus
    
    @property
    def is_alive(self):
        return self.current_toughness > 0
    
    def can_attack(self, current_turn: int) -> bool:
        """Check if this ally can attack."""
        if not self.is_alive:
            return False
        if self.tapped:
            return False
        if self.has_attacked_this_turn:
            return False
        # Summoning sickness: can't attack on turn entered unless Charge
        if self.turn_entered == current_turn and not self.has_charge:
            return False
        return True
    
    def has_keyword(self, kw: Keyword) -> bool:
        """Check if ally has a keyword (permanent or temporary)."""
        return kw in self.card.keywords or kw in self.temporary_keywords
    
    @property
    def has_charge(self):
        return self.has_keyword(Keyword.CHARGE)
    
    @property
    def has_ranged(self):
        return self.has_keyword(Keyword.RANGED)
    
    @property
    def has_trample(self):
        return self.has_keyword(Keyword.TRAMPLE)
    
    @property
    def has_brutal(self):
        return self.has_keyword(Keyword.BRUTAL)
    
    @property
    def has_intimidate(self):
        return self.has_keyword(Keyword.INTIMIDATE)
    
    @property
    def has_wraith_form(self):
        return self.has_keyword(Keyword.WRATH_FORM)
    
    def add_temp_keyword(self, kw: Keyword):
        """Add a temporary keyword (persists until clear_temp_bonuses)."""
        self.temporary_keywords.add(kw)
    
    def clear_temp_bonuses(self):
        """Clear all temporary modifiers (end of turn)."""
        self.power_bonus = 0
        self.toughness_bonus = 0
        self.temporary_keywords.clear()
    
    def can_move(self) -> bool:
        """Check if this ally can move. Movement costs the action."""
        if not self.is_alive:
            return False
        if self.tapped:
            return False
        if self.has_moved_this_turn:
            return False
        if self.has_attacked_this_turn:
            return False  # Can't move after attacking
        return True
    
    def take_damage(self, amount: int):
        """Apply persistent damage."""
        self.damage += amount
        self.current_toughness = max(0, self.card.toughness - self.damage)
    
    def heal(self, amount: int):
        """Heal damage."""
        healed = min(amount, self.damage)
        self.damage -= healed
        self.current_toughness = self.card.toughness - self.damage
        return healed
    
    def __repr__(self):
        dmg = f"[{self.damage}dmg]" if self.damage > 0 else ""
        tapped = "T" if self.tapped else ""
        atk = "A" if self.has_attacked_this_turn else ""
        return f"{self.card.name}({self.card.power}/{self.current_toughness}){dmg}{tapped}{atk}"
