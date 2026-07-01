"""
Rohan (Free Peoples) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_rohan_hero() -> Card:
    """Create Theoden, King of Rohan."""
    return Card(
        name="Theoden, King of Rohan",
        faction=Faction.ROHAN,
        card_type=CardType.HERO,
        cost=0,
        power=4,
        toughness=4,
        rarity="Legendary",
        rules_text="Forth Eorlingas!: Exhaust to give Rohan allies at location +1 Power and Charge.\n"
                   "King of the Horse-lords: Mount Artifacts cost 2 less for Rohan allies.",
        flavor_text='"Arise, arise, Riders of Theoden! Fell deeds awake, fire and slaughter!"',
        creature_types=["Man", "Noble"],
        keywords=[Keyword.CHARGE],
    )


# Pre-constructed 30-card Rohan deck
ROHAN_DECK = [
    # 4x Westfold Shepherd (1-cost, Muster)
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),

    # 4x Rider of Rohan (2-cost, Charge)
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),

    # 3x Rohirrim Archer (3-cost, Ranged, Death-cry)
    Card(name="Rohirrim Archer", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Archer"],
         rules_text="Ranged. Death-cry: deal 1 damage to destroyer on death.",
         keywords=[Keyword.RANGED, Keyword.DEATH_CRY]),
    Card(name="Rohirrim Archer", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Archer"],
         rules_text="Ranged. Death-cry: deal 1 damage to destroyer on death.",
         keywords=[Keyword.RANGED, Keyword.DEATH_CRY]),
    Card(name="Rohirrim Archer", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Archer"],
         rules_text="Ranged. Death-cry: deal 1 damage to destroyer on death.",
         keywords=[Keyword.RANGED, Keyword.DEATH_CRY]),

    # 2x Rider of the Mark (4-cost, Charge, Death-cry)
    Card(name="Rider of the Mark", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=4, power=3, toughness=3, creature_types=["Man", "Rider"],
         rules_text="Charge. Death-cry: next Rohan ally costs 2 less.",
         keywords=[Keyword.CHARGE, Keyword.DEATH_CRY]),
    Card(name="Rider of the Mark", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=4, power=3, toughness=3, creature_types=["Man", "Rider"],
         rules_text="Charge. Death-cry: next Rohan ally costs 2 less.",
         keywords=[Keyword.CHARGE, Keyword.DEATH_CRY]),

    # 1x Eomer, Third Marshal (5-cost)
    Card(name="Eomer, Third Marshal of the Mark", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=5, power=5, toughness=3, creature_types=["Man", "Marshal"],
         rules_text="Charge. On attack: create 2/1 Rider token at location.",
         keywords=[Keyword.CHARGE]),

    # 1x Helm Hammerhand's Descendant (6-cost)
    Card(name="Helm Hammerhand's Descendant", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=6, power=5, toughness=4, creature_types=["Man", "Champion"],
         rules_text="Charge. On attack vs location: +2 damage to location defense.",
         keywords=[Keyword.CHARGE]),

    # Events (6)
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),
    Card(name="Westfold Shepherd", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=1, power=1, toughness=1, creature_types=["Man", "Civilian"],
         rules_text="Muster: Sacrifice to create a 2/1 Rider token with Charge.",
         keywords=[Keyword.MUSTER]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    Card(name="Rider of Rohan", faction=Faction.ROHAN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Rider"],
         rules_text="Charge. Cavalry: +1 Power with Mount attached.",
         keywords=[Keyword.CHARGE]),
    # Events (6)
    Card(name="Ride of the Rohirrim", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=3, rules_text="Target Rohan ally gains Charge and +2 Power. If already Charge, +3 instead."),
    Card(name="Ride of the Rohirrim", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=3, rules_text="Target Rohan ally gains Charge and +2 Power. If already Charge, +3 instead."),
    Card(name="Ride of the Rohirrim", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=3, rules_text="Target Rohan ally gains Charge and +2 Power. If already Charge, +3 instead."),
    Card(name="Muster the Rohirrim", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=4, rules_text="Create three 2/1 Rider tokens with Charge. Deploy to any locations you control."),
    Card(name="Muster the Rohirrim", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=4, rules_text="Create three 2/1 Rider tokens with Charge. Deploy to any locations you control."),
    Card(name="Forth Eorlingas!", faction=Faction.ROHAN, card_type=CardType.EVENT,
         cost=6, rules_text="Up to 3 Rohan allies gain Charge and +2 Power. They take 1 damage after turn."),

    # Artifacts (2)
    Card(name="Snowmane", faction=Faction.ROHAN, card_type=CardType.ARTIFACT,
         cost=3, rules_text="Attach to Rohan ally. Bearer gains Charge. If Theoden, +1/+1."),
    Card(name="The Horn of Helm Hammerhand", faction=Faction.ROHAN, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Once/game: sacrifice for 2 damage to all enemies at location. Rohan allies +1 Power."),

    # Locations (2)
    Card(name="Helm's Deep", faction=Faction.ROHAN, card_type=CardType.LOCATION,
         cost=4, defense=6, rules_text="Allies here have +2 Toughness. When flipped: 2 damage to all attackers here."),
    Card(name="Helm's Deep", faction=Faction.ROHAN, card_type=CardType.LOCATION,
         cost=4, defense=6, rules_text="Allies here have +2 Toughness. When flipped: 2 damage to all attackers here."),
]
