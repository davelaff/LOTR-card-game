"""
Isengard (Shadow) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_isengard_hero() -> Card:
    """Create Saruman of Many Colors."""
    return Card(
        name="Saruman of Many Colors",
        faction=Faction.ISENGARD,
        card_type=CardType.HERO,
        cost=0,
        power=3,
        toughness=5,
        rarity="Legendary",
        rules_text="The Voice of Saruman: Exhaust, target enemy at contested location gets -2 Power.\n"
                   "Industrial Might: Sacrifice Uruk-hai to gain 3 WP (Isengard cards only).",
        flavor_text='"For I am Saruman the Wise, Saruman Ring-maker, Saruman of Many Colors!"',
        creature_types=["Wizard"],
        keywords=[Keyword.INDUSTRY],
    )


# Pre-constructed 30-card Isengard deck
ISENGARD_DECK = [
    # 4x Isengard Sapper (2-cost, Sunder)
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),

    # 4x Uruk-hai Soldier (3-cost, Formation)
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),

    # 4x Uruk-hai Pikeman (3-cost)
    Card(name="Uruk-hai Pikeman", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=2, toughness=4, creature_types=["Uruk-hai"],
         rules_text="Phalanx: +2 Power with 2+ other Uruk-hai at location. Formation.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Pikeman", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=2, toughness=4, creature_types=["Uruk-hai"],
         rules_text="Phalanx: +2 Power with 2+ other Uruk-hai at location. Formation.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Pikeman", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=2, toughness=4, creature_types=["Uruk-hai"],
         rules_text="Phalanx: +2 Power with 2+ other Uruk-hai at location. Formation.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Pikeman", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=2, toughness=4, creature_types=["Uruk-hai"],
         rules_text="Phalanx: +2 Power with 2+ other Uruk-hai at location. Formation.",
         keywords=[Keyword.FORMATION]),

    # 2x Uruk-hai Berserker (4-cost, Charge + Frenzy)
    Card(name="Uruk-hai Berserker", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=4, power=5, toughness=2, creature_types=["Uruk-hai"],
         rules_text="Charge. Frenzy: +2 Power on attack, then takes 1 damage.",
         keywords=[Keyword.CHARGE]),
    Card(name="Uruk-hai Berserker", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=4, power=5, toughness=2, creature_types=["Uruk-hai"],
         rules_text="Charge. Frenzy: +2 Power on attack, then takes 1 damage.",
         keywords=[Keyword.CHARGE]),

    # 1x Ugluk (5-cost)
    Card(name="Ugluk, Uruk-hai Captain", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=5, power=4, toughness=4, creature_types=["Uruk-hai", "Captain"],
         rules_text="Discipline: Uruk-hai here cannot have Power reduced. On attack: other Uruk-hai +1 Power.",
         keywords=[Keyword.FORMATION]),

    # 1x Isengard Siege Tower (6-cost)
    Card(name="Isengard Siege Tower", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=6, power=3, toughness=6, creature_types=["Construct"],
         rules_text="Siege: Cannot attack allies, can attack locations directly.",
         keywords=[Keyword.SIEGE]),

    # Events (6)
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),
    Card(name="Isengard Sapper", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=2, power=1, toughness=2, creature_types=["Orc"],
         rules_text="Sunder: On enter, destroy Artifact cost 3 or less. Industry: sacrifice for 2 WP.",
         keywords=[Keyword.SUNDER, Keyword.INDUSTRY]),
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),
    Card(name="Uruk-hai Soldier", faction=Faction.ISENGARD, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Uruk-hai"],
         rules_text="Formation: +1 Toughness while another Uruk-hai at same location.",
         keywords=[Keyword.FORMATION]),
    # Events (6)
    Card(name="The White Hand", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Uruk-hai gains +2/+2. If at contested, destroy enemy Artifact there."),
    Card(name="The White Hand", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Uruk-hai gains +2/+2. If at contested, destroy enemy Artifact there."),
    Card(name="The White Hand", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=3, rules_text="Target Uruk-hai gains +2/+2. If at contested, destroy enemy Artifact there."),
    Card(name="Isengard Unleashed", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=5, rules_text="Reveal top 6, put Uruk-hai allies into play with Charge."),
    Card(name="Isengard Unleashed", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=5, rules_text="Reveal top 6, put Uruk-hai allies into play with Charge."),
    Card(name="A New Power Rises", faction=Faction.ISENGARD, card_type=CardType.EVENT,
         cost=7, rules_text="Destroy all Artifacts at location. Create 3/3 Uruk-hai tokens for each."),

    # Artifacts (2)
    Card(name="Uruk-hai Battle-blade", faction=Faction.ISENGARD, card_type=CardType.ARTIFACT,
        cost=3, rules_text="Bearer +2 Power. Cannot be destroyed by Free Peoples effects."),
    Card(name="Uruk-hai Battle-blade", faction=Faction.ISENGARD, card_type=CardType.ARTIFACT,
        cost=3, rules_text="Bearer +2 Power. Cannot be destroyed by Free Peoples effects."),

    # Locations (2)
    Card(name="Orthanc", faction=Faction.ISENGARD, card_type=CardType.LOCATION,
         cost=5, defense=5, rules_text="Uruk-hai cost 1 less. When flipped: flipper gains 3 WP."),
    Card(name="Orthanc", faction=Faction.ISENGARD, card_type=CardType.LOCATION,
         cost=5, defense=5, rules_text="Uruk-hai cost 1 less. When flipped: flipper gains 3 WP."),
]
