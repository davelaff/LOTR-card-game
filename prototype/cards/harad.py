"""
Harad (Shadow) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_harad_hero() -> Card:
    """Create The Golden King of Harad."""
    return Card(
        name="The Golden King of Harad",
        faction=Faction.HARAD,
        card_type=CardType.HERO,
        cost=0,
        power=2,
        toughness=5,
        rarity="Legendary",
        rules_text="Serpent-lord: Exhaust to gain 2 WP (Harad allies only).\n"
                   "Tribute to the Dark Lord: At start of turn, if you control a Mumak, +1 Corruption and draw.",
        flavor_text='"The Men of Harad came, tall and dark, with eyes like coals."',
        creature_types=["Man", "Noble"],
        keywords=[Keyword.RAMP],
    )


# Pre-constructed 30-card Harad deck
HARAD_DECK = [
    # 4x Haradrim Archer (2-cost, Ranged + Scout)
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),

    # 4x Easterling Spearman (3-cost, Intimidate)
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),

    # 3x Haradrim Cavalry (4-cost, Charge)
    Card(name="Haradrim Cavalry", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=4, power=4, toughness=3, creature_types=["Man", "Haradrim"],
         rules_text="Charge. Desert Wind: +1 Power and free moves with a Mumak.",
         keywords=[Keyword.CHARGE]),
    Card(name="Haradrim Cavalry", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=4, power=4, toughness=3, creature_types=["Man", "Haradrim"],
         rules_text="Charge. Desert Wind: +1 Power and free moves with a Mumak.",
         keywords=[Keyword.CHARGE]),
    Card(name="Haradrim Cavalry", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=4, power=4, toughness=3, creature_types=["Man", "Haradrim"],
         rules_text="Charge. Desert Wind: +1 Power and free moves with a Mumak.",
         keywords=[Keyword.CHARGE]),

    # 2x Serpent Guard (5-cost)
    Card(name="Serpent Guard", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=5, power=3, toughness=5, creature_types=["Man", "Haradrim"],
         rules_text="Bodyguard: Hero in back line cannot be targeted. Intimidate.",
         keywords=[Keyword.INTIMIDATE]),
    Card(name="Serpent Guard", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=5, power=3, toughness=5, creature_types=["Man", "Haradrim"],
         rules_text="Bodyguard: Hero in back line cannot be targeted. Intimidate.",
         keywords=[Keyword.INTIMIDATE]),

    # 1x Mumak of Harad (7-cost, Trample + Carry)
    Card(name="Mumak of Harad", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=7, power=7, toughness=7, creature_types=["Mumak"],
         rules_text="Trample. War-beast: can carry 2 Haradrim. Massive: immovable.",
         keywords=[Keyword.TRAMPLE, Keyword.CARRY]),

    # 1x Mumakil War-Leader (8-cost)
    Card(name="Mumakil War-Leader", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=8, power=8, toughness=8, creature_types=["Mumak"],
         rules_text="Trample. Carry 3. Stampede: on destroy, 1 damage to all other enemies at location.",
         keywords=[Keyword.TRAMPLE, Keyword.CARRY, Keyword.STAMPEDE]),

    # Additional allies (5 extra copies for ally-heavy deck)
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Haradrim Archer", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=2, power=2, toughness=1, creature_types=["Man", "Haradrim", "Archer"],
         rules_text="Ranged. Scout: Foresight 1 on enter.",
         keywords=[Keyword.RANGED, Keyword.SCOUT]),
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),
    Card(name="Easterling Spearman", faction=Faction.HARAD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=2, creature_types=["Man", "Easterling"],
         rules_text="Phalanx: +1 Toughness with another ally at location. Intimidate: on attack, target -1 Power.",
         keywords=[Keyword.INTIMIDATE]),
    # Events (6)
    Card(name="The Serpent's Coil", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Haradrim gains Intimidate. If Mumak, gains it permanently."),
    Card(name="The Serpent's Coil", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Haradrim gains Intimidate. If Mumak, gains it permanently."),
    Card(name="The Serpent's Coil", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Haradrim gains Intimidate. If Mumak, gains it permanently."),
    Card(name="From the South and East", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=5, rules_text="Search top 6 for a Harad ally, put into play with Charge."),
    Card(name="From the South and East", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=5, rules_text="Search top 6 for a Harad ally, put into play with Charge."),
    Card(name="The War-beasts Rampage", faction=Faction.HARAD, card_type=CardType.EVENT,
         cost=6, rules_text="Target Mumak gains +2 Power and attacks twice. Deals Power as Influence damage."),

    # Artifacts (2)
    Card(name="Scimitar of the Serpent-lords", faction=Faction.HARAD, card_type=CardType.ARTIFACT,
         cost=3, rules_text="Bearer +1 Power. Combat damage deals +1 at start of enemy's next turn."),
    Card(name="The War-tower of the Mumak", faction=Faction.HARAD, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Attach to Mumak. Carry +1 ally. Carried allies gain Ranged."),

    # Locations (2)
    Card(name="The Harad Road", faction=Faction.HARAD, card_type=CardType.LOCATION,
         cost=4, defense=3, rules_text="Harad allies move freely between your locations. When flipped: flipper plays Harad ally from hand."),
    Card(name="The Harad Road", faction=Faction.HARAD, card_type=CardType.LOCATION,
         cost=4, defense=3, rules_text="Harad allies move freely between your locations. When flipped: flipper plays Harad ally from hand."),
]
