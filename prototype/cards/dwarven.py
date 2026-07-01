"""
Dwarven (Free Peoples) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword


def create_dwarven_hero() -> Card:
    """Create Gimli, Son of Gloin."""
    return Card(
        name="Gimli, Son of Gloin",
        faction=Faction.DWARVEN,
        card_type=CardType.HERO,
        cost=0,
        power=4,
        toughness=4,
        rarity="Legendary",
        rules_text="Grudge: Mark enemy that damaged a Dwarf. +2 Power vs marked enemy.\n"
                   "Axe of the Dwarves: Destroying Grudge target creates Treasure token.",
        flavor_text='"Baruk Khazad! Khazad ai-menu!"',
        creature_types=["Dwarf", "Warrior"],
        keywords=[Keyword.GRUDGE],
    )


# Pre-constructed 30-card Dwarven deck
DWARVEN_DECK = [
    # 4x Dwarven Axe-bearer (2-cost, Fortitude 1)
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),

    # 4x Dwarven Miner (2-cost)
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),

    # 4x Shield-bearer of Erebor (3-cost)
    Card(name="Shield-bearer of Erebor", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=3, power=1, toughness=5, creature_types=["Dwarf", "Guard"],
         rules_text="Iron Wall: While in front line, enemy cannot target your back line."),
    Card(name="Shield-bearer of Erebor", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=3, power=1, toughness=5, creature_types=["Dwarf", "Guard"],
         rules_text="Iron Wall: While in front line, enemy cannot target your back line."),
    Card(name="Shield-bearer of Erebor", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=3, power=1, toughness=5, creature_types=["Dwarf", "Guard"],
         rules_text="Iron Wall: While in front line, enemy cannot target your back line."),
    Card(name="Shield-bearer of Erebor", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=3, power=1, toughness=5, creature_types=["Dwarf", "Guard"],
         rules_text="Iron Wall: While in front line, enemy cannot target your back line."),

    # 2x Dwarven Forge-master (4-cost)
    Card(name="Dwarven Forge-master", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=4, power=3, toughness=4, creature_types=["Dwarf", "Smith"],
         rules_text="Temper: Exhaust to give equipped Dwarf +2 Toughness. Artisan: attach Artifact on enter."),
    Card(name="Dwarven Forge-master", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=4, power=3, toughness=4, creature_types=["Dwarf", "Smith"],
         rules_text="Temper: Exhaust to give equipped Dwarf +2 Toughness. Artisan: attach Artifact on enter."),

    # 1x Dain Ironfoot (5-cost)
    Card(name="Dain Ironfoot", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=5, power=4, toughness=5, creature_types=["Dwarf", "Lord"],
         rules_text="King Under the Mountain: Search top 7 for 2 Dwarves on enter. Baruk Khazad: exhaust, +1 Power to Dwarves at location."),

    # 1x Vault Warden of Khazad-dum (6-cost)
    Card(name="Vault Warden of Khazad-dum", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=6, power=4, toughness=8, creature_types=["Dwarf", "Warden"],
         rules_text="Fortitude 2. +2 Power while you control a Treasure token.",
         keywords=[Keyword.RESILIENCE]),

    # Events (6)
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Dwarven Axe-bearer", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Dwarf", "Warrior"],
         rules_text="Fortitude 1: Damage dealt to this ally is reduced by 1.",
         keywords=[Keyword.RESILIENCE]),
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),
    Card(name="Dwarven Miner", faction=Faction.DWARVEN, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Dwarf", "Miner"],
         rules_text="Prospect: On enter, create a Treasure token."),
    # Events (6)
    Card(name="To Me! O My Kinsfolk!", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=3, rules_text="Reveal top 5. Put all Dwarven allies into hand. Rest on bottom."),
    Card(name="To Me! O My Kinsfolk!", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=3, rules_text="Reveal top 5. Put all Dwarven allies into hand. Rest on bottom."),
    Card(name="To Me! O My Kinsfolk!", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=3, rules_text="Reveal top 5. Put all Dwarven allies into hand. Rest on bottom."),
    Card(name="The Ire of the Mountain", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=5, rules_text="Destroy target Artifact or Location. Draw 2 if you control a Dwarf."),
    Card(name="The Ire of the Mountain", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=5, rules_text="Destroy target Artifact or Location. Draw 2 if you control a Dwarf."),
    Card(name="The Hammer Falls", faction=Faction.DWARVEN, card_type=CardType.EVENT,
         cost=7, rules_text="4 damage to all allies at target location. Dwarves take no damage."),

    # Artifacts (2)
    Card(name="The Arkenstone", faction=Faction.DWARVEN, card_type=CardType.ARTIFACT,
         cost=5, rules_text="Attach to Dwarven Hero. Treasures generate 3 WP. Once/game: create 3 Treasures."),
    Card(name="Mithril Coat", faction=Faction.DWARVEN, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Bearer +3 Toughness. Immune to Nazgul Fear. Retains Stealth."),

    # Locations (2)
    Card(name="Erebor", faction=Faction.DWARVEN, card_type=CardType.LOCATION,
         cost=5, defense=5, rules_text="Treasures generate +1 WP. When flipped: flipper creates 2 Treasures."),
    Card(name="Erebor", faction=Faction.DWARVEN, card_type=CardType.LOCATION,
         cost=5, defense=5, rules_text="Treasures generate +1 WP. When flipped: flipper creates 2 Treasures."),
]
