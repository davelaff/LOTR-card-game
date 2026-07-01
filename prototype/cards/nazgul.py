"""
Nazgul (Shadow) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_nazgul_hero() -> Card:
    """Create The Witch-king of Angmar."""
    return Card(
        name="The Witch-king of Angmar",
        faction=Faction.NAZGUL,
        card_type=CardType.HERO,
        cost=0,
        power=5,
        toughness=4,
        rarity="Legendary",
        rules_text="Fear 2: Enemy allies at this location have -2 Power.\n"
                   "Morgul-blade: Once/game, exhaust to deal 4 damage, prevent healing for rest of game.\n"
                   "No Man Can Kill Me: Damage from Human allies reduced by 2.",
        flavor_text='"Come not between the Nazgul and his prey!"',
        creature_types=["Nazgul", "Wraith"],
        keywords=[Keyword.FEAR, Keyword.TERRIFY],
    )


# Pre-constructed 30-card Nazgul deck
NAZGUL_DECK = [
    # 6x Barrow-wight (2-cost, Fear 1, cheap for the faction)
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),

    # 6x Nazgul Wraith (5-cost)
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),

    # 2x The Dwimmerlaik (6-cost, Fear 2 + Drain Will)
    Card(name="The Dwimmerlaik", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=6, power=4, toughness=4, creature_types=["Nazgul", "Wraith"],
         rules_text="Fear 2. Wraith Form. Drain Will: exhaust to permanently -1/-1 to target enemy at location.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR, Keyword.DOMINATE]),
    Card(name="The Dwimmerlaik", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=6, power=4, toughness=4, creature_types=["Nazgul", "Wraith"],
         rules_text="Fear 2. Wraith Form. Drain Will: exhaust to permanently -1/-1 to target enemy at location.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR, Keyword.DOMINATE]),

    # 1x The Shadow Host (8-cost)
    Card(name="The Shadow Host", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=8, power=6, toughness=5, creature_types=["Wraith"],
         rules_text="Fear 3. Wraith Form. On enter: all enemies -1 Power. Oathbreaker: cannot die to combat.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR, Keyword.OATHBREAKER]),

    # Additional allies (9 total Barrow-wight, 8 total Nazgul Wraith)
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Barrow-wight", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=2, power=2, toughness=3, creature_types=["Wraith"],
         rules_text="Fear 1. Cold Grasp: When enemy dies here, may exile it and draw.",
         keywords=[Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    Card(name="Nazgul Wraith", faction=Faction.NAZGUL, card_type=CardType.ALLY,
         cost=5, power=4, toughness=3, creature_types=["Nazgul", "Wraith"],
         rules_text="Wraith Form: immune to physical damage. Fear 1. The Nine: +1 Power with another Nazgul.",
         keywords=[Keyword.WRATH_FORM, Keyword.FEAR]),
    # Events (6)
    Card(name="All Shall Fade", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=5, rules_text="Target gains Wraith Form. If Nazgul, deal 3 damage to enemy at same location."),
    Card(name="All Shall Fade", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=5, rules_text="Target gains Wraith Form. If Nazgul, deal 3 damage to enemy at same location."),
    Card(name="All Shall Fade", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=5, rules_text="Target gains Wraith Form. If Nazgul, deal 3 damage to enemy at same location."),
    Card(name="The Ring Is Mine", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=4, rules_text="FP chooses: activate Ring (you draw 2) or lose 3 Influence. +1 Corruption either way."),
    Card(name="The Ring Is Mine", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=4, rules_text="FP chooses: activate Ring (you draw 2) or lose 3 Influence. +1 Corruption either way."),
    Card(name="The Ring Is Mine", faction=Faction.NAZGUL, card_type=CardType.EVENT,
         cost=4, rules_text="FP chooses: activate Ring (you draw 2) or lose 3 Influence. +1 Corruption either way."),

    # Artifacts (2)
    Card(name="Morgul-blade", faction=Faction.NAZGUL, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Bearer +1 Power. Once/game: exhaust for 3 damage, prevent healing rest of game, lose 1 Influence."),
    Card(name="Morgul-blade", faction=Faction.NAZGUL, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Bearer +1 Power. Once/game: exhaust for 3 damage, prevent healing rest of game, lose 1 Influence."),

    # Locations (2)
    Card(name="Minas Morgul", faction=Faction.NAZGUL, card_type=CardType.LOCATION,
         cost=5, defense=4, rules_text="Nazgul here +1 Power and Fear 1. When flipped: flipper gains 2 Corruption."),
    Card(name="Minas Morgul", faction=Faction.NAZGUL, card_type=CardType.LOCATION,
         cost=5, defense=4, rules_text="Nazgul here +1 Power and Fear 1. When flipped: flipper gains 2 Corruption."),
]
