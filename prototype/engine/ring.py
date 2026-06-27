"""
The One Ring mechanic — corruption track, activations, theft.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Ring:
    """The One Ring — always present in every match."""
    corruption: int = 0
    bearer: str = "fp"  # "fp" or "shadow"
    fp_activated_this_turn: bool = False
    shadow_activated_this_turn: bool = False
    shadow_bearer_turns: int = 0  # Turns Shadow has borne the Ring
    
    CORRUPTION_WARNING = 15
    CORRUPTION_DANGER = 20
    CORRUPTION_LOSS = 30
    
    def add_corruption(self, amount: int):
        """Add corruption counters."""
        self.corruption = min(30, self.corruption + amount)
    
    def check_corruption_loss(self) -> Optional[str]:
        """Check if corruption causes a loss. Returns losing player or None."""
        if self.corruption >= self.CORRUPTION_LOSS:
            return self.bearer
        return None
    
    def get_corruption_status(self) -> str:
        """Get a text description of current corruption level."""
        if self.corruption >= self.CORRUPTION_LOSS:
            return "The Ring has consumed its bearer! GAME OVER."
        elif self.corruption >= self.CORRUPTION_DANGER:
            return f"⚠ DANGER: {self.corruption}/30 — The Ring is close to consuming its bearer!"
        elif self.corruption >= self.CORRUPTION_WARNING:
            return f"⚡ WARNING: {self.corruption}/30 — The Ring grows heavy."
        else:
            return f"Corruption: {self.corruption}/30"
    
    def can_activate_fp(self) -> bool:
        """Can Free Peoples activate the Ring right now?"""
        return self.bearer == "fp" and not self.fp_activated_this_turn
    
    def can_activate_shadow(self) -> bool:
        """Can Shadow activate the Ring right now?"""
        return self.bearer == "shadow" and not self.shadow_activated_this_turn
    
    def activate_fp(self, choice: str):
        """Activate the Ring for Free Peoples. Returns the effect description."""
        self.fp_activated_this_turn = True
        self.add_corruption(2)
        return choice
    
    def activate_shadow(self, choice: str):
        """Activate the Ring for Shadow. Returns the effect description."""
        self.shadow_activated_this_turn = True
        self.add_corruption(1)  # Shadow bears the Ring more naturally; +1 vs FP's +2
        return choice
    
    def steal_by_shadow(self):
        """Shadow steals the Ring by killing the FP Hero."""
        self.bearer = "shadow"
        self.shadow_bearer_turns = 0
        self.fp_activated_this_turn = False
        self.shadow_activated_this_turn = False
    
    def recover_by_fp(self):
        """Free Peoples recovers the Ring by killing the Shadow Hero."""
        self.bearer = "fp"
        self.fp_activated_this_turn = False
        self.shadow_activated_this_turn = False
    
    def end_turn(self, player: str):
        """Handle end-of-turn effects."""
        if player == "shadow" and self.bearer == "shadow":
            self.shadow_bearer_turns += 1
            # 0.5 passive corruption per turn = +1 every 2 turns
            if self.shadow_bearer_turns % 2 == 0:
                self.add_corruption(1)
    
    def start_turn(self):
        """Reset per-turn activation flags."""
        self.fp_activated_this_turn = False
        self.shadow_activated_this_turn = False
    
    @property
    def corruption_track_str(self) -> str:
        """Visual corruption track."""
        bar = ""
        for i in range(10, 40, 10):
            if self.corruption >= i:
                bar += "█"
            elif self.corruption >= i - 5:
                bar += "▒"
            else:
                bar += "░"
        return f"[{bar}] {self.corruption}/30"
