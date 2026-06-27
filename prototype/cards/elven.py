"""
Elven (Free Peoples) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_elven_hero() -> Card:
    """Create Galadriel, Lady of Light."""
    return Card(
        name="Galadriel, Lady of Light",
        faction=Faction.ELVEN,
        card_type=CardType.HERO,
        cost=0,
        power=2,
        toughness=3,
        rarity="Legendary",
        rules_text="Mirror of Galadriel: Foresight 3 (look at top 3, draw 1).\n"
                   "The Light of Earendil: Nazgul allies at this location have -1 Power.",
        flavor_text='"I pass the test. I will diminish, and go into the West."',
        creature_types=["Elf", "Noble"],
        keywords=[Keyword.FORESIGHT],
    )


# Pre-constructed 30-card Elven deck
ELVEN_DECK = [
    # 4x Elven Archer (2-cost, Ranged)
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),

    # 4x Galadhrim Sentinel (2-cost)
    Card(name="Galadhrim Sentinel", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Elf", "Guard"],
         rules_text="Watcher of the Wood: On enemy enter, reveal top card; if Elven, deal 1 damage."),
    Card(name="Galadhrim Sentinel", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Elf", "Guard"],
         rules_text="Watcher of the Wood: On enemy enter, reveal top card; if Elven, deal 1 damage."),
    Card(name="Galadhrim Sentinel", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Elf", "Guard"],
         rules_text="Watcher of the Wood: On enemy enter, reveal top card; if Elven, deal 1 damage."),
    Card(name="Galadhrim Sentinel", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Elf", "Guard"],
         rules_text="Watcher of the Wood: On enemy enter, reveal top card; if Elven, deal 1 damage."),

    # 4x Marchwarden of Lorien (3-cost)
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),

    # 2x Elven Smith of Eregion (4-cost)
    Card(name="Elven Smith of Eregion", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=4, power=2, toughness=3, creature_types=["Elf", "Smith"],
         rules_text="Ancient Craft: Exhaust to reduce next Artifact cost by 2."),
    Card(name="Elven Smith of Eregion", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=4, power=2, toughness=3, creature_types=["Elf", "Smith"],
         rules_text="Ancient Craft: Exhaust to reduce next Artifact cost by 2."),

    # 1x Elrond, Master of Rivendell (5-cost)
    Card(name="Elrond, Master of Rivendell", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=5, power=3, toughness=4, creature_types=["Elf", "Lord"],
         rules_text="Vilya: Exhaust to scry 3, grab Elven card. +2 max hand size.",
         keywords=[Keyword.FORESIGHT]),

    # 1x Glorfindel (6-cost)
    Card(name="Glorfindel, Lord of the Golden Flower", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=6, power=5, toughness=3, creature_types=["Elf", "Champion"],
         rules_text="+2 Power vs Nazgul at contested location. Grace: prevent all first damage.",
         keywords=[Keyword.GRACE]),

    # Events (6)
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Elven Archer", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Elf", "Archer"],
         rules_text="Ranged: Can attack from the back line.", keywords=[Keyword.RANGED]),
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),
    Card(name="Marchwarden of Lorien", faction=Faction.ELVEN, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Elf", "Warden"],
         rules_text="Foresight 1 on enter. Grace: Prevent 1 first damage per turn.",
         keywords=[Keyword.FORESIGHT, Keyword.GRACE]),
    # Events (6)
    Card(name="Lembas", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=2, rules_text="Heal 3 damage. +1 Power until end of turn."),
    Card(name="Lembas", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=2, rules_text="Heal 3 damage. +1 Power until end of turn."),
    Card(name="Lembas", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=2, rules_text="Heal 3 damage. +1 Power until end of turn."),
    Card(name="The Light of the Evenstar", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=4, rules_text="Target gains Stealth and +1/+1. Heal 1 at end of turn."),
    Card(name="The Light of the Evenstar", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=4, rules_text="Target gains Stealth and +1/+1. Heal 1 at end of turn."),
    Card(name="The Last Alliance", faction=Faction.ELVEN, card_type=CardType.EVENT,
         cost=7, rules_text="Reveal top 8. Put Elven/Gondor allies into play at locations."),

    # Artifacts (2)
    Card(name="The Phial of Galadriel", faction=Faction.ELVEN, card_type=CardType.ARTIFACT,
         cost=3, rules_text="Once/game: exhaust for 3 damage to Nazgul/Orc. Bearer gains Stealth. Fear immune."),
    Card(name="Bow of the Galadhrim", faction=Faction.ELVEN, card_type=CardType.ARTIFACT,
         cost=3, rules_text="Bearer gains Ranged. +1 Power when attacking from back line."),

    # Locations (2)
    Card(name="Rivendell", faction=Faction.ELVEN, card_type=CardType.LOCATION,
         cost=3, defense=3, rules_text="Start of turn: Foresight 1. When flipped: flipper draws 2."),
    Card(name="Rivendell", faction=Faction.ELVEN, card_type=CardType.LOCATION,
         cost=3, defense=3, rules_text="Start of turn: Foresight 1. When flipped: flipper draws 2."),
]
