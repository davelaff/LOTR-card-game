"""
Hobbit / Fellowship (Free Peoples) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_hobbit_hero() -> Card:
    """Create Frodo Baggins, Ring-bearer."""
    return Card(
        name="Frodo Baggins, Ring-bearer",
        faction=Faction.HOBBIT,
        card_type=CardType.HERO,
        cost=0,
        power=1,
        toughness=2,
        rarity="Legendary",
        rules_text="The Weight of the Ring: You gain 0 Corruption when activating the Ring.\n"
                   "I Will Take It: Once/game, exhaust to activate Ring with no Corruption cost.",
        flavor_text='"I will take the Ring to Mordor — though I do not know the way."',
        creature_types=["Hobbit"],
        keywords=[Keyword.FELLOWSHIP],
    )


# Pre-constructed 30-card Hobbit deck
HOBBIT_DECK = [
    # 4x Hobbit Bounder (1-cost)
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),

    # 4x Meriadoc Brandybuck (2-cost)
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),

    # 4x Peregrin Took (2-cost)
    Card(name="Peregrin Took", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Hobbit"],
         rules_text="Fool of a Took: Exhaust, scry 1. Ent-draught: +2 Power at 3+ Toughness."),
    Card(name="Peregrin Took", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Hobbit"],
         rules_text="Fool of a Took: Exhaust, scry 1. Ent-draught: +2 Power at 3+ Toughness."),
    Card(name="Peregrin Took", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Hobbit"],
         rules_text="Fool of a Took: Exhaust, scry 1. Ent-draught: +2 Power at 3+ Toughness."),
    Card(name="Peregrin Took", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Hobbit"],
         rules_text="Fool of a Took: Exhaust, scry 1. Ent-draught: +2 Power at 3+ Toughness."),

    # 2x Farmer Maggot (3-cost)
    Card(name="Farmer Maggot", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Hobbit"],
         rules_text="No Trespassers: Enemy taking this location takes 1 damage. Steadfast.",
         keywords=[Keyword.STEADFAST]),
    Card(name="Farmer Maggot", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Hobbit"],
         rules_text="No Trespassers: Enemy taking this location takes 1 damage. Steadfast.",
         keywords=[Keyword.STEADFAST]),

    # 2x Rosie Cotton (3-cost)
    Card(name="Rosie Cotton", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=3, power=1, toughness=3, creature_types=["Hobbit"],
         rules_text="Simple Comfort: Exhaust to heal 1 from Hobbit (2 if Sam). Resilience: +1 Tough when Ring activated.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Rosie Cotton", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=3, power=1, toughness=3, creature_types=["Hobbit"],
         rules_text="Simple Comfort: Exhaust to heal 1 from Hobbit (2 if Sam). Resilience: +1 Tough when Ring activated.",
         keywords=[Keyword.RESILIENCE]),

    # Events (6)
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),
    Card(name="Hobbit Bounder", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Shirriff: On enter, look at top card of deck, may bottom it."),
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),
    Card(name="Meriadoc Brandybuck", faction=Faction.HOBBIT, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Hobbit"],
         rules_text="Fellowship: Stealth while with another FP ally. Conspirator: exhaust to protect Hobbit from effects.",
         keywords=[Keyword.FELLOWSHIP, Keyword.STEALTH]),
    # Events (6)
    Card(name="The Straight Road", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=2, rules_text="Target gains Stealth until end of turn. Draw a card if still controlled."),
    Card(name="The Straight Road", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=2, rules_text="Target gains Stealth until end of turn. Draw a card if still controlled."),
    Card(name="The Straight Road", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=2, rules_text="Target gains Stealth until end of turn. Draw a card if still controlled."),
    Card(name="The Straight Road", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=2, rules_text="Target gains Stealth until end of turn. Draw a card if still controlled."),
    Card(name="I Will Not Say the Day Is Done", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=5, rules_text="Remove up to 3 Corruption. Draw a card for each removed."),
    Card(name="I Will Not Say the Day Is Done", faction=Faction.HOBBIT, card_type=CardType.EVENT,
         cost=5, rules_text="Remove up to 3 Corruption. Draw a card for each removed."),

    # Artifacts (2)
    Card(name="Sting", faction=Faction.HOBBIT, card_type=CardType.ARTIFACT,
         cost=2, rules_text="Attach to Hobbit. +1 Power. +2 Power vs Orcs. Glows Blue: look at top card anytime."),
    Card(name="Sting", faction=Faction.HOBBIT, card_type=CardType.ARTIFACT,
         cost=2, rules_text="Attach to Hobbit. +1 Power. +2 Power vs Orcs. Glows Blue: look at top card anytime."),

    # Locations (2)
    Card(name="The Shire", faction=Faction.HOBBIT, card_type=CardType.LOCATION,
         cost=2, defense=2, rules_text="Hobbits here +1 Tough, Fear immune. When flipped: create 1/1 Hobbit Militia with Charge."),
    Card(name="The Shire", faction=Faction.HOBBIT, card_type=CardType.LOCATION,
         cost=2, defense=2, rules_text="Hobbits here +1 Tough, Fear immune. When flipped: create 1/1 Hobbit Militia with Charge."),
]
