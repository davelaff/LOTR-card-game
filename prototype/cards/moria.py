"""
Moria (Shadow) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_moria_hero() -> Card:
    """Create Gorbag, Captain of the Deeps."""
    return Card(
        name="Gorbag, Captain of the Deeps",
        faction=Faction.MORIA,
        card_type=CardType.HERO,
        cost=0,
        power=3,
        toughness=4,
        rarity="Legendary",
        rules_text="Ambush Commander: Pay 2 WP, put a Goblin from hand into contested location.\n"
                   "Scavenger: When ally dies at this location, create 1/1 Goblin token.",
        flavor_text="\"What's this? A fight? Let's make it a proper one.\"",
        creature_types=["Orc", "Commander"],
        keywords=[Keyword.AMBUSH],
    )


# Pre-constructed 30-card Moria deck
MORIA_DECK = [
    # 4x Moria Goblin (1-cost, Darkness)
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),

    # 4x Goblin Sneak (2-cost, Ambush)
    Card(name="Goblin Sneak", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Ambush. Skulking: On Ambush entry, deal 1 damage to enemy at location.",
         keywords=[Keyword.AMBUSH]),
    Card(name="Goblin Sneak", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Ambush. Skulking: On Ambush entry, deal 1 damage to enemy at location.",
         keywords=[Keyword.AMBUSH]),
    Card(name="Goblin Sneak", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Ambush. Skulking: On Ambush entry, deal 1 damage to enemy at location.",
         keywords=[Keyword.AMBUSH]),
    Card(name="Goblin Sneak", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Ambush. Skulking: On Ambush entry, deal 1 damage to enemy at location.",
         keywords=[Keyword.AMBUSH]),

    # 4x Goblin Archer (2-cost, Ranged)
    Card(name="Goblin Archer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Goblin", "Archer"],
         rules_text="Ranged. Poisoned Arrow: Damage from back line prevents healing.",
         keywords=[Keyword.RANGED]),
    Card(name="Goblin Archer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Goblin", "Archer"],
         rules_text="Ranged. Poisoned Arrow: Damage from back line prevents healing.",
         keywords=[Keyword.RANGED]),
    Card(name="Goblin Archer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Goblin", "Archer"],
         rules_text="Ranged. Poisoned Arrow: Damage from back line prevents healing.",
         keywords=[Keyword.RANGED]),
    Card(name="Goblin Archer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Goblin", "Archer"],
         rules_text="Ranged. Poisoned Arrow: Damage from back line prevents healing.",
         keywords=[Keyword.RANGED]),

    # 2x Moria Drummer (4-cost)
    Card(name="Moria Drummer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=4, power=2, toughness=3, creature_types=["Goblin"],
         rules_text="Drums in the Deep: Exhaust, +1 Power to Goblins at location. Doom: on enter, return Goblin from discard."),
    Card(name="Moria Drummer", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=4, power=2, toughness=3, creature_types=["Goblin"],
         rules_text="Drums in the Deep: Exhaust, +1 Power to Goblins at location. Doom: on enter, return Goblin from discard."),

    # 1x Cave Troll (5-cost)
    Card(name="Cave Troll", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=5, power=6, toughness=5, creature_types=["Troll"],
         rules_text="Tunnel: Move to adjacent location. Massive: immovable. Club and Chain: on attack, 1 damage to another enemy.",
         keywords=[Keyword.TUNNEL]),

    # 1x The Watcher in the Water (7-cost)
    Card(name="The Watcher in the Water", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=7, power=5, toughness=7, creature_types=["Horror"],
         rules_text="Ambush. On enter: 1 damage to up to 3 enemies. Darkness: +2 Power while alone.",
         keywords=[Keyword.AMBUSH, Keyword.DARKNESS]),

    # 1x The Balrog of Moria (9-cost)
    Card(name="The Balrog of Moria", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=9, power=9, toughness=9, creature_types=["Demon"],
         rules_text="Durin's Bane: 3 damage to all others on enter. Fear 3. Whip: 1 damage to enemies leaving.",
         keywords=[Keyword.FEAR, Keyword.TERRIFY]),

    # Events (6)
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),
    Card(name="Moria Goblin", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Darkness: +1 Power while no enemies at this location.",
         keywords=[Keyword.DARKNESS]),
    Card(name="Goblin Sneak", faction=Faction.MORIA, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Goblin"],
         rules_text="Ambush. Skulking: On Ambush entry, deal 1 damage to enemy at location.",
         keywords=[Keyword.AMBUSH]),
    # Events (6)
    Card(name="Drums in the Deep", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=3, rules_text="Return up to 2 Goblins from discard to hand. Create 1/1 Goblin token."),
    Card(name="Drums in the Deep", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=3, rules_text="Return up to 2 Goblins from discard to hand. Create 1/1 Goblin token."),
    Card(name="Drums in the Deep", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=3, rules_text="Return up to 2 Goblins from discard to hand. Create 1/1 Goblin token."),
    Card(name="They Are Coming", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=5, rules_text="Put up to 3 Goblins from hand into location via Ambush. They gain Charge."),
    Card(name="They Are Coming", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=5, rules_text="Put up to 3 Goblins from hand into location via Ambush. They gain Charge."),
    Card(name="The Chasm Opens", faction=Faction.MORIA, card_type=CardType.EVENT,
         cost=6, rules_text="Move all Goblins to any locations (ignore adjacency). 2 damage to enemies at busiest target."),

    # Artifacts (2)
    Card(name="Goblin-forged Blade", faction=Faction.MORIA, card_type=CardType.ARTIFACT,
         cost=2, rules_text="Bearer +1 Power. Combat damage deals +1 damage at end of turn."),
    Card(name="Durin's Axe", faction=Faction.MORIA, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Bearer +2 Power, +1 Toughness. Gains Grudge vs Dwarves."),

    # Locations (2)
    Card(name="The Mines of Moria", faction=Faction.MORIA, card_type=CardType.LOCATION,
         cost=4, defense=3, rules_text="Goblins here have Ambush, Darkness doubled. When flipped: flipper searches for Artifact."),
    Card(name="The Mines of Moria", faction=Faction.MORIA, card_type=CardType.LOCATION,
         cost=4, defense=3, rules_text="Goblins here have Ambush, Darkness doubled. When flipped: flipper searches for Artifact."),
]
