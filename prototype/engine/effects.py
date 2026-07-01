"""
Ability resolution and keyword effects for the LOTR Card Battle Game.
"""

from typing import Optional
from engine.card import BoardAlly, Card, CardType, Keyword, Faction
from engine.board import Board, LocationSlot


class EffectResolver:
    """Handles card ability resolutions."""
    
    def __init__(self, game):
        self.game = game
    
    def resolve_on_enter(self, ally: BoardAlly, player: str):
        """Resolve 'When this ally enters play' effects."""
        card = ally.card
        msgs = []
        
        # Swarm: create tokens
        if Keyword.SWARM in card.keywords:
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                token = create_orc_token()
                turn = self.game.fp_player.turn_number if player == "fp" else self.game.shadow_player.turn_number
                token_ally = BoardAlly(
                    card=token,
                    current_toughness=token.toughness,
                    turn_entered=turn,
                )
                loc = self.game.board.get_location(loc_index)
                loc.add_ally(token_ally, player, "front")
                msgs.append(f"Swarm: Created {token.name}!")
        
        # Fortify: add defense to location
        if Keyword.FORTIFY in card.keywords:
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                if loc.location_card:
                    loc.fortify_bonus += 1
                    loc.current_defense += 1
                    msgs.append(f"Fortify: {loc.location_card.name} gains +1 Defense!")
        
        # Scout / Foresight
        if Keyword.SCOUT in card.keywords:
            player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
            if player_state.deck:
                top = player_state.deck[-1]
                msgs.append(f"Scout: Top card is {top.name}. Keeping on top.")
        
        # Foresight
        if Keyword.FORESIGHT in card.keywords:
            player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
            if player_state.deck:
                msgs.append(f"Foresight: Glimpsed the future. (Simplified)")
        
        # Watchman Vigilant ability
        if card.name == "Watchman of Minas Tirith":
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                if loc.location_card:
                    loc.fortify_bonus += 1
                    loc.current_defense += 1
                    msgs.append(f"Vigilant: {loc.location_card.name} gains +1 Defense!")
        
        # Orc War-band Swarm
        if card.name == "Orc War-band":
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                token = create_orc_token()
                turn = self.game.fp_player.turn_number if player == "fp" else self.game.shadow_player.turn_number
                token_ally = BoardAlly(
                    card=token,
                    current_toughness=token.toughness,
                    turn_entered=turn,
                )
                loc = self.game.board.get_location(loc_index)
                loc.add_ally(token_ally, player, "front")
                msgs.append(f"Swarm: Created {token.name}!")
        
        # Grishnakh Insurrection
        if card.name == "Grishnákh, Orc-Captain":
            msgs.append("Insurrection: Orc allies gain +1 Power this turn!")
        
        # Imrahil rally
        if card.name == "Imrahil, Prince of Dol Amroth":
            healed = 0
            for loc in self.game.board.locations:
                for a in loc.get_allies(player):
                    if a is not ally and a.damage > 0:
                        a.heal(1)
                        healed += 1
            if healed:
                msgs.append(f"Rally: Healed 1 damage from {healed} Gondor allies!")
        
        # Great Beast of Gorgoroth - deal 2 damage to enemy allies
        if card.name == "The Great Beast of Gorgoroth":
            enemy = "shadow" if player == "fp" else "fp"
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                for enemy_ally in loc.get_allies(enemy):
                    enemy_ally.take_damage(2)
                msgs.append("Terror of Gorgoroth: 2 damage to all enemies at this location!")
        
        # The Balrog entry damage
        if card.name == "The Balrog of Moria":
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                for ally_set in [loc.get_allies("fp"), loc.get_allies("shadow")]:
                    for a in ally_set:
                        if a is not ally:
                            a.take_damage(3)
                msgs.append("Durin's Bane: 3 damage to ALL other allies at this location!")
        
        # The Watcher in the Water entry
        if card.name == "The Watcher in the Water":
            enemy = "shadow" if player == "fp" else "fp"
            loc_index = self.game.board.find_ally_location(ally, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                count = 0
                for enemy_ally in loc.get_allies(enemy)[:3]:
                    enemy_ally.take_damage(1)
                    count += 1
                if count:
                    msgs.append(f"Many Arms: 1 damage to {count} enemies!")
        
        # The Shadow Host entry
        if card.name == "The Shadow Host":
            for loc in self.game.board.locations:
                for enemy_ally in loc.get_allies("fp"):
                    # -1 Power is temporary, simplified as notification
                    pass
            msgs.append("Army of the Dead: All enemies lose 1 Power this turn!")
        
        # Dwarven Miner - create Treasure token
        if card.name == "Dwarven Miner":
            msgs.append("Prospect: Created a Treasure token! (WP boost later)")
        
        # Hobbit Bounder
        if card.name == "Hobbit Bounder":
            player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
            if player_state.deck:
                msgs.append("Shirriff: Looked at top card of deck.")
        
        return msgs
    
    def resolve_on_destroy(self, ally: BoardAlly, player: str):
        """Resolve 'When this ally is destroyed' effects."""
        msgs = []
        card = ally.card
        
        # Mordor Orc: add 1 corruption on death
        if card.name == "Mordor Orc":
            self.game.ring.add_corruption(1)
            msgs.append(f"Mordor Orc's death adds +1 Corruption!")
        
        # Death-cry keyword
        if Keyword.DEATH_CRY in card.keywords:
            msgs.append(f"{card.name}'s Death-cry triggers! (Simplified)")
        
        return msgs
    
    def resolve_hero_ability(self, hero: BoardAlly, player: str) -> list:
        """Resolve a Hero's activated ability. Returns list of messages."""
        msgs = []
        card = hero.card
        player_state = self.game.fp_player if player == "fp" else self.game.shadow_player
        faction = card.faction
        
        # --- Aragorn: Healing Hands ---
        if card.name == "Aragorn, Heir of Isildur":
            hero.tapped = True
            loc_index = self.game.board.find_ally_location(hero, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                candidates = [a for a in loc.get_allies(player) if a.damage > 0 and a is not hero]
                if candidates:
                    target = candidates[0]
                    healed = target.heal(2)
                    msgs.append(f"Aragorn heals {target.card.name} for {healed} damage!")
                else:
                    msgs.append("No wounded allies at location to heal.")
            hero.has_used_ability_this_turn = True
        
        # --- Gothmog: The Swarm Rises ---
        elif card.name == "Gothmog, Lieutenant of Morgul":
            if player_state.spend_willpower(2):
                loc_index = self.game.board.find_ally_location(hero, player)
                if loc_index is not None and loc_index >= 0:
                    token = create_orc_token()
                    token_ally = BoardAlly(
                        card=token,
                        current_toughness=token.toughness,
                        turn_entered=self.game.current_turn_number,
                    )
                    self.game.board.get_location(loc_index).add_ally(token_ally, player, "front")
                    msgs.append("Gothmog creates an Orc token!")
                    hero.has_used_ability_this_turn = True
                else:
                    msgs.append("Gothmog must be at a location.")
            else:
                msgs.append("Not enough Willpower! Need 2 WP.")
        
        # --- Galadriel: Mirror of Galadriel (Foresight 3) ---
        elif card.name == "Galadriel, Lady of Light":
            hero.tapped = True
            drawn = player_state.draw_cards(3)
            msgs.append(f"Galadriel's Mirror reveals the future! Drew {len(drawn)} cards.")
            hero.has_used_ability_this_turn = True
        
        # --- Gimli: Grudge ---
        elif card.name == "Gimli, Son of Gloin":
            hero.tapped = True
            # Mark an enemy ally (simplified: just give +2 Power vs next attack)
            msgs.append("Gimli marks an enemy with Grudge! (+2 Power vs that enemy)")
            hero.has_used_ability_this_turn = True
        
        # --- Theoden: Forth Eorlingas! ---
        elif card.name == "Theoden, King of Rohan":
            hero.tapped = True
            loc_index = self.game.board.find_ally_location(hero, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                rohan_count = 0
                for ally in loc.get_allies(player):
                    if ally.card.faction == Faction.ROHAN or ally.card.name == "Rider of Rohan":
                        rohan_count += 1
                msgs.append(f"Theoden rallies {rohan_count} Rohan allies! (+1 Power and Charge)")
            hero.has_used_ability_this_turn = True
        
        # --- Frodo: I Will Take It (once/game, activate Ring with no Corruption) ---
        elif card.name == "Frodo Baggins, Ring-bearer":
            hero.tapped = True
            if self.game.ring.bearer == "fp" and not self.game.ring.fp_activated_this_turn:
                # Activate without corruption
                drawn = player_state.draw_cards(2)
                msgs.append(f"Frodo takes the Ring! Drew {len(drawn)} cards. (No Corruption!)")
            else:
                msgs.append("Ring already activated or not held by FP.")
            hero.has_used_ability_this_turn = True
        
        # --- Saruman: The Voice of Saruman ---
        elif card.name == "Saruman of Many Colors":
            hero.tapped = True
            loc_index = self.game.board.find_ally_location(hero, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                if loc.is_contested():
                    enemy = "shadow" if player == "fp" else "fp"
                    for enemy_ally in loc.get_allies(enemy):
                        msgs.append(f"Saruman's voice weakens {enemy_ally.card.name}! (-2 Power)")
                        break
                else:
                    msgs.append("Saruman's location is not contested.")
            hero.has_used_ability_this_turn = True
        
        # --- Gorbag: Ambush Commander ---
        elif card.name == "Gorbag, Captain of the Deeps":
            if player_state.willpower_pool >= 2:
                # Find a Goblin in hand
                goblin = None
                for c in player_state.hand:
                    if c.card_type == CardType.ALLY and "Goblin" in c.creature_types:
                        goblin = c
                        break
                if goblin and player_state.spend_willpower(2):
                    player_state.play_card(goblin)
                    goblin_ally = BoardAlly(
                        card=goblin,
                        current_toughness=goblin.toughness,
                        turn_entered=player_state.turn_number,
                    )
                    # Deploy to contested location
                    for loc in self.game.board.locations:
                        if loc.is_contested():
                            loc.add_ally(goblin_ally, player, "front")
                            msgs.append(f"Gorbag deploys {goblin.name} via Ambush!")
                            break
                    else:
                        # Fallback: deploy to hero's location
                        loc_index = self.game.board.find_ally_location(hero, player)
                        if loc_index is not None and loc_index >= 0:
                            self.game.board.get_location(loc_index).add_ally(goblin_ally, player, "front")
                            msgs.append(f"Gorbag deploys {goblin.name}!")
                    hero.has_used_ability_this_turn = True
                else:
                    msgs.append("No Goblin in hand or not enough WP!")
            else:
                msgs.append("Not enough Willpower! Need 2 WP.")
        
        # --- Golden King of Harad: Serpent-lord (gain 2 WP) ---
        elif card.name == "The Golden King of Harad":
            hero.tapped = True
            player_state.add_willpower(2)
            msgs.append(f"The Golden King grants +2 Willpower! (now {player_state.willpower_pool})")
            hero.has_used_ability_this_turn = True
        
        # --- Witch-king: Morgul-blade (once/game) ---
        elif card.name == "The Witch-king of Angmar":
            hero.tapped = True
            loc_index = self.game.board.find_ally_location(hero, player)
            if loc_index is not None and loc_index >= 0:
                loc = self.game.board.get_location(loc_index)
                enemy = "shadow" if player == "fp" else "fp"
                targets = loc.get_allies(enemy)
                if targets:
                    target = targets[0]
                    target.take_damage(4)
                    msgs.append(f"Witch-king's Morgul-blade strikes {target.card.name}! (4 damage, cannot heal)")
                else:
                    msgs.append("No enemies at location to strike!")
            hero.has_used_ability_this_turn = True
        
        else:
            # Generic hero ability
            hero.tapped = True
            msgs.append(f"{hero.card.name} uses their ability (simplified).")
            hero.has_used_ability_this_turn = True
        
        return msgs
    
    def resolve_ring_activation_fp(self, choice: str) -> list:
        """Resolve a Free Peoples Ring activation."""
        msgs = []
        ring = self.game.ring
        if ring.bearer != "fp":
            msgs.append(f"Free Peoples do not bear the Ring! (Bearer: {ring.bearer})")
            return msgs
        if ring.fp_activated_this_turn:
            msgs.append("Ring already activated this turn! (Once per turn only.)")
            return msgs
        
        self.game.ring.activate_fp(choice)
        msgs.append(f"Ring activated! +2 Corruption (now {self.game.ring.corruption}/30)")
        
        if choice == "draw":
            drawn = self.game.fp_player.draw_cards(2)
            msgs.append(f"Drew {len(drawn)} cards.")
        elif choice == "willpower":
            self.game.fp_player.add_willpower(2)
            msgs.append(f"Gained +2 Willpower (now {self.game.fp_player.willpower_pool}).")
        elif choice == "stealth":
            msgs.append("Ring-bearer gains Stealth until end of turn.")
        elif choice == "bolster":
            if self.game.fp_player.hero:
                loc_index = self.game.board.find_ally_location(self.game.fp_player.hero, "fp")
                if loc_index is not None and loc_index >= 0:
                    loc = self.game.board.get_location(loc_index)
                    if loc.location_card:
                        loc.current_defense += 2
                        msgs.append(f"Bolster: {loc.location_card.name} gains +2 Defense!")
        
        return msgs
    
    def resolve_ring_activation_shadow(self, choice: str) -> list:
        """Resolve a Shadow Ring activation."""
        msgs = []
        if not self.game.ring.can_activate_shadow():
            msgs.append("Ring already activated this turn!")
            return msgs
        if self.game.ring.bearer != "shadow":
            msgs.append("Shadow does not bear the Ring!")
            return msgs
        
        self.game.ring.activate_shadow(choice)
        msgs.append(f"Ring activated - Shadow Dominion! +2 Corruption (now {self.game.ring.corruption}/30)")
        
        if choice == "drain":
            self.game.fp_player.willpower_pool = max(0, self.game.fp_player.willpower_pool - 2)
            self.game.shadow_player.add_willpower(1)
            msgs.append("Drained 2 WP from Free Peoples! Shadow gains +1 WP.")
        elif choice == "corrupt":
            self.game.ring.add_corruption(1)
            msgs.append(f"Inflicted +1 Corruption (now {self.game.ring.corruption}/30)")
        elif choice == "dominate":
            msgs.append("Dominated an enemy ally (simplified - not implemented).")
        elif choice == "fortify":
            if self.game.shadow_player.hero:
                loc_index = self.game.board.find_ally_location(self.game.shadow_player.hero, "shadow")
                if loc_index is not None and loc_index >= 0:
                    loc = self.game.board.get_location(loc_index)
                    if loc.location_card:
                        loc.current_defense += 3
                        msgs.append(f"Fortified {loc.location_card.name} with +3 Defense!")
        
        return msgs


def create_orc_token() -> Card:
    """Create a 1/1 Orc token."""
    return Card(
        name="Orc Token",
        faction=Faction.MORDOR,
        card_type=CardType.ALLY,
        cost=0,
        power=1,
        toughness=1,
        creature_types=["Orc"],
        rules_text="Token creature.",
    )


def create_rider_token() -> Card:
    """Create a 2/1 Rider token with Charge."""
    return Card(
        name="Rider Token",
        faction=Faction.ROHAN,
        card_type=CardType.ALLY,
        cost=0,
        power=2,
        toughness=1,
        creature_types=["Man", "Rider"],
        rules_text="Charge. Token creature.",
        keywords=[Keyword.CHARGE],
    )


def create_goblin_token() -> Card:
    """Create a 1/1 Goblin token."""
    return Card(
        name="Goblin Token",
        faction=Faction.MORIA,
        card_type=CardType.ALLY,
        cost=0,
        power=1,
        toughness=1,
        creature_types=["Goblin"],
        rules_text="Token creature.",
    )


def create_uruk_hai_token(power: int = 3, toughness: int = 3) -> Card:
    """Create an Uruk-hai token (default 3/3)."""
    return Card(
        name="Uruk-hai Token",
        faction=Faction.ISENGARD,
        card_type=CardType.ALLY,
        cost=0,
        power=power,
        toughness=toughness,
        creature_types=["Uruk-hai"],
        rules_text="Token creature.",
    )
