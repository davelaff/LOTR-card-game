"""
Board state — locations, ally positioning, front/back lines.
"""

from dataclasses import dataclass, field
from typing import Optional
from engine.card import Card, BoardAlly, CardType, Keyword

MAX_ROW_CAPACITY = 4

@dataclass
class LocationSlot:
    """A single location slot on the board."""
    index: int  # 0, 1, or 2 (Slot 1, 2, 3)
    location_card: Optional[Card] = None
    current_defense: int = 0
    controller: Optional[str] = None  # "fp" or "shadow" or None
    fortify_bonus: int = 0
    
    # Allies at this location per player
    fp_front: list = field(default_factory=list)  # List[BoardAlly]
    fp_back: list = field(default_factory=list)
    shadow_front: list = field(default_factory=list)
    shadow_back: list = field(default_factory=list)
    
    def is_empty(self):
        return self.location_card is None
    
    def is_controlled_by(self, player: str):
        return self.controller == player
    
    def is_contested(self) -> bool:
        """A location is contested when both players have allies there."""
        fp_allies = len(self.fp_front) + len(self.fp_back)
        shadow_allies = len(self.shadow_front) + len(self.shadow_back)
        return fp_allies > 0 and shadow_allies > 0
    
    def get_allies(self, player: str):
        """Get all allies for a player at this location."""
        if player == "fp":
            return self.fp_front + self.fp_back
        return self.shadow_front + self.shadow_back
    
    def get_front_line(self, player: str):
        if player == "fp":
            return self.fp_front
        return self.shadow_front
    
    def get_back_line(self, player: str):
        if player == "fp":
            return self.fp_back
        return self.shadow_back
    
    def has_front_line(self, player: str) -> bool:
        """Check if a player has any allies in the front line."""
        front = self.get_front_line(player)
        return len(front) > 0
    
    def add_ally(self, ally: BoardAlly, player: str, row: str = "front"):
        """Add an ally to this location. Returns True if successful."""
        if row == "front":
            target = self.get_front_line(player)
        else:
            target = self.get_back_line(player)
        
        if len(target) >= MAX_ROW_CAPACITY:
            return False
        target.append(ally)
        return True
    
    def remove_ally(self, ally: BoardAlly, player: str) -> bool:
        """Remove an ally from this location."""
        for lst in [self.get_front_line(player), self.get_back_line(player)]:
            for i, a in enumerate(lst):
                if a is ally:
                    lst.pop(i)
                    return True
        return False
    
    def find_ally_row(self, ally: BoardAlly, player: str) -> Optional[str]:
        """Find which row an ally is in."""
        if ally in self.get_front_line(player):
            return "front"
        if ally in self.get_back_line(player):
            return "back"
        return None
    
    def valid_attack_targets(self, attacker: BoardAlly, attacker_player: str):
        """Get valid attack targets for an attacker at this location."""
        target_player = "shadow" if attacker_player == "fp" else "fp"
        attacker_row = self.find_ally_row(attacker, attacker_player)
        targets = []
        
        # Can always attack front line enemies
        for ally in self.get_front_line(target_player):
            if ally.is_alive:
                targets.append(("ally_front", ally))
        
        # Can attack back line if: attacker has Ranged, OR no front-line enemies
        if attacker.has_ranged or not self.has_front_line(target_player):
            for ally in self.get_back_line(target_player):
                if ally.is_alive:
                    targets.append(("ally_back", ally))
        
        # Can attack the location if no front-line enemies
        if not self.has_front_line(target_player) and self.location_card and not self.is_empty():
            targets.append(("location", self))
        
        return targets
    
    def valid_targets_for_player_action(self, player: str) -> list:
        """Get all attackable targets for all allies of a player."""
        result = []
        for row_name, row in [("front", self.get_front_line(player)), ("back", self.get_back_line(player))]:
            for ally in row:
                targets = self.valid_attack_targets(ally, player)
                if targets:
                    result.append((ally, targets))
        return result
    
    def deal_defense_damage(self, amount: int):
        """Deal damage to location defense. Returns True if location flips."""
        self.current_defense -= amount
        if self.current_defense <= 0:
            # Flip the location
            old_controller = self.controller
            self.controller = "shadow" if old_controller == "fp" else "fp"
            self.current_defense = self.location_card.defense + self.fortify_bonus
            return True
        return False
    
    def __repr__(self):
        if self.is_empty():
            return f"[Loc {self.index+1}: Empty]"
        ctrl = "FP" if self.controller == "fp" else "SH"
        cont = " (Contested)" if self.is_contested() else ""
        return f"[Loc {self.index+1}: {self.location_card.name}(Def {self.current_defense}) {ctrl}{cont}]"


@dataclass
class Board:
    """The game board with 3 location slots and 2 deployment zones."""
    locations: list = field(default_factory=list)  # 3 LocationSlots
    
    # Deployment zones
    fp_deployment: list = field(default_factory=list)  # List[BoardAlly]
    shadow_deployment: list = field(default_factory=list)
    
    def __post_init__(self):
        if not self.locations:
            from engine.card import Card, CardType, Faction
            # Slot 0 (left), Slot 1 (center - Open Field), Slot 2 (right)
            open_field = Card(
                name="Open Field",
                faction=Faction.NEUTRAL,
                card_type=CardType.LOCATION,
                cost=0,
                defense=5,
                rules_text="A neutral battlefield. No effect."
            )
            self.locations = [
                LocationSlot(index=0),
                LocationSlot(index=1, location_card=open_field, current_defense=5, controller=None),
                LocationSlot(index=2),
            ]
    
    def get_location(self, index: int) -> LocationSlot:
        if 0 <= index < 3:
            return self.locations[index]
        return None
    
    def play_location(self, card: Card, player: str, slot_index: int) -> bool:
        """Play a location card into a slot."""
        loc = self.get_location(slot_index)
        if loc is None or not loc.is_empty():
            return False
        loc.location_card = card
        loc.current_defense = card.defense
        loc.controller = player
        return True
    
    def deploy_ally(self, ally: BoardAlly, player: str) -> bool:
        """Deploy an ally to the deployment zone."""
        zone = self.fp_deployment if player == "fp" else self.shadow_deployment
        zone.append(ally)
        return True
    
    def move_ally_to_location(self, ally: BoardAlly, player: str, 
                               location_index: int, row: str = "front") -> bool:
        """Move an ally from deployment to a location."""
        zone = self.fp_deployment if player == "fp" else self.shadow_deployment
        if ally in zone:
            zone.remove(ally)
        else:
            # Also check if ally is at another location
            for loc in self.locations:
                if loc.remove_ally(ally, player):
                    break
            else:
                return False  # Ally not found
        
        loc = self.get_location(location_index)
        return loc.add_ally(ally, player, row)
    
    def move_ally_between_locations(self, ally: BoardAlly, player: str,
                                     from_index: int, to_index: int, 
                                     to_row: str = "front") -> bool:
        """Move an ally from one location to another."""
        from_loc = self.get_location(from_index)
        to_loc = self.get_location(to_index)
        if from_loc is None or to_loc is None:
            return False
        if not from_loc.remove_ally(ally, player):
            return False
        return to_loc.add_ally(ally, player, to_row)
    
    def move_ally_between_rows(self, ally: BoardAlly, player: str,
                                 location_index: int, target_row: str) -> bool:
        """Move an ally between front and back line at same location."""
        loc = self.get_location(location_index)
        if loc is None:
            return False
        current_row = loc.find_ally_row(ally, player)
        if current_row is None or current_row == target_row:
            return False
        if not loc.remove_ally(ally, player):
            return False
        return loc.add_ally(ally, player, target_row)
    
    def remove_ally(self, ally: BoardAlly, player: str) -> bool:
        """Remove an ally from anywhere on the board."""
        zone = self.fp_deployment if player == "fp" else self.shadow_deployment
        if ally in zone:
            zone.remove(ally)
            return True
        for loc in self.locations:
            if loc.remove_ally(ally, player):
                return True
        return False
    
    def find_ally_location(self, ally: BoardAlly, player: str) -> Optional[int]:
        """Find which location index an ally is at. Returns -1 for deployment zone."""
        zone = self.fp_deployment if player == "fp" else self.shadow_deployment
        if ally in zone:
            return -1
        for i, loc in enumerate(self.locations):
            if ally in loc.get_allies(player):
                return i
        return None
    
    def get_all_allies(self, player: str) -> list:
        """Get all allies on the board for a player."""
        zone = self.fp_deployment if player == "fp" else self.shadow_deployment
        result = list(zone)
        for loc in self.locations:
            result.extend(loc.get_allies(player))
        return result
    
    def get_allies_at_location(self, player: str, loc_index: int) -> list:
        """Get all allies for a player at a specific location."""
        loc = self.get_location(loc_index)
        if loc:
            return loc.get_allies(player)
        return []
    
    def get_front_line_at(self, player: str, loc_index: int) -> list:
        loc = self.get_location(loc_index)
        if loc:
            return loc.get_front_line(player)
        return []
    
    def get_back_line_at(self, player: str, loc_index: int) -> list:
        loc = self.get_location(loc_index)
        if loc:
            return loc.get_back_line(player)
        return []
