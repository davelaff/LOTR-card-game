"""
Mordor (Shadow) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword

def create_mordor_hero() -> Card:
    """Create Gothmog, Lieutenant of Morgul."""
    return Card(
        name="Gothmog, Lieutenant of Morgul",
        faction=Faction.MORDOR,
        card_type=CardType.HERO,
        cost=0,
        power=4,
        toughness=4,
        rarity="Legendary",
        rules_text="The Swarm Rises: Pay 2 WP to create a 1/1 Orc token at Gothmog's location.\n"
                   "Sacrifice the Weak: Sacrifice an Orc for +2 Power until end of turn.",
        flavor_text='"The Lieutenant of the Tower of Barad-dûr."',
        creature_types=["Orc", "Commander"],
        keywords=[],
    )


# Pre-constructed 30-card Mordor deck
MORDOR_DECK = [
    # 3x Mordor Orc (1-cost)
    Card(name="Mordor Orc", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Expendable: On death, add +1 Corruption."),
    Card(name="Mordor Orc", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Expendable: On death, add +1 Corruption."),
    Card(name="Mordor Orc", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Expendable: On death, add +1 Corruption."),
    
    # 3x Orc Warrior (1-cost filler)
    Card(name="Orc Warrior", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="A common soldier of Mordor."),
    Card(name="Orc Warrior", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="A common soldier of Mordor."),
    Card(name="Orc Warrior", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Orc"],
         rules_text="A common soldier of Mordor."),
    
    # 3x Orc Archer (2-cost, Ranged)
    Card(name="Orc Archer", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Orc Archer", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Orc Archer", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    
    # 2x Mordor Spear-Orc (2-cost filler)
    Card(name="Mordor Spear-Orc", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Orc"],
         rules_text="Vicious but fragile."),
    Card(name="Mordor Spear-Orc", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Orc"],
         rules_text="Vicious but fragile."),
    
    # 2x Orc Taskmaster (3-cost)
    Card(name="Orc Taskmaster", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=2, creature_types=["Orc"],
         rules_text="Whip the Rabble: Exhaust to give target Orc +2 Power."),
    Card(name="Orc Taskmaster", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=2, creature_types=["Orc"],
         rules_text="Whip the Rabble: Exhaust to give target Orc +2 Power."),
    
    # 3x Orc Marauder (3-cost filler)
    Card(name="Orc Marauder", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=3, creature_types=["Orc"],
         rules_text="A battle-hardened Orc raider."),
    Card(name="Orc Marauder", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=3, creature_types=["Orc"],
         rules_text="A battle-hardened Orc raider."),
    Card(name="Orc Marauder", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=3, creature_types=["Orc"],
         rules_text="A battle-hardened Orc raider."),
    
    # 2x Orc War-band (4-cost)
    Card(name="Orc War-band", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=4, power=3, toughness=3, creature_types=["Orc"],
         rules_text="Swarm: Create 1/1 Orc token on enter.", keywords=[Keyword.SWARM]),
    Card(name="Orc War-band", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=4, power=3, toughness=3, creature_types=["Orc"],
         rules_text="Swarm: Create 1/1 Orc token on enter.", keywords=[Keyword.SWARM]),
    
    # 1x Grishnákh (5-cost)
    Card(name="Grishnákh, Orc-Captain", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Orc", "Captain"],
         rules_text="Orc allies at location have +1 Power. Insurrection on enter."),
    
    # 1x Mordor Troll (6-cost)
    Card(name="Mordor Troll", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=6, power=6, toughness=6, creature_types=["Troll"],
         rules_text="Olog-hai: Needs another Orc to attack. Brutal: +1 damage.",
         keywords=[Keyword.BRUTAL]),
    
    # 1x The Great Beast of Gorgoroth (8-cost)
    Card(name="The Great Beast of Gorgoroth", faction=Faction.MORDOR, card_type=CardType.ALLY,
         cost=8, power=7, toughness=7, creature_types=["Beast"],
         rules_text="Trample. On enter: 2 damage to all enemies at location.",
         keywords=[Keyword.TRAMPLE]),
    
    # Events
    Card(name="The Shadow Spreads", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=2, rules_text="+1 Corruption. Create 1/1 Orc token."),
    Card(name="The Shadow Spreads", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=2, rules_text="+1 Corruption. Create 1/1 Orc token."),
    Card(name="Shadow's Reach", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=3, rules_text="Deal 2 Burn damage to opponent's Influence. +1 Corruption."),
    Card(name="Shadow's Reach", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=3, rules_text="Deal 2 Burn damage to opponent's Influence. +1 Corruption."),
    Card(name="The Lidless Eye", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=4, rules_text="Look at opponent's hand, discard one. +1 Corruption."),
    Card(name="The Fires of Mount Doom", faction=Faction.MORDOR, card_type=CardType.EVENT,
         cost=8, rules_text="3 damage to all enemies. +2 Corruption."),
    
    # Artifacts
    Card(name="Grond, Hammer of the Underworld", faction=Faction.MORDOR, card_type=CardType.ARTIFACT,
         cost=7, rules_text="Battering Ram: Exhaust to reduce location defense by 3."),
    Card(name="Blade of the Morgul-host", faction=Faction.MORDOR, card_type=CardType.ARTIFACT,
         cost=3, rules_text="Bearer +2 Power. Damage prevents healing."),
    
    # Locations
    Card(name="The Black Gate", faction=Faction.MORDOR, card_type=CardType.LOCATION,
         cost=4, defense=4, rules_text="Orc allies cost 1 less Willpower."),
    Card(name="The Black Gate", faction=Faction.MORDOR, card_type=CardType.LOCATION,
         cost=4, defense=4, rules_text="Orc allies cost 1 less Willpower."),
]
