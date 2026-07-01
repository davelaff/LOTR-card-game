"""
Gondor (Free Peoples) card definitions.
"""

from engine.card import Card, CardType, Faction, Keyword

def create_gondor_hero() -> Card:
    """Create Aragorn, Heir of Isildur."""
    return Card(
        name="Aragorn, Heir of Isildur",
        faction=Faction.GONDOR,
        card_type=CardType.HERO,
        cost=0,
        power=4,
        toughness=5,
        rarity="Legendary",
        rules_text="Healing Hands: Tap to heal 2 damage from target ally at same location.\n"
                   "The King's Standard: Allies at locations you control with 3+ Def have +1/+1.",
        flavor_text='"The hands of the king are the hands of a healer."',
        creature_types=["Man", "Noble"],
        keywords=[],
    )

def create_gondor_cards() -> list:
    """Create all Gondor card definitions."""
    cards = []
    
    # Allies
    cards.append(Card(
        name="Watchman of Minas Tirith",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=1,
        power=1,
        toughness=2,
        rarity="Common",
        rules_text="Vigilant: When this ally enters play, add +1 Defense to target location you control.",
        creature_types=["Man", "Soldier"],
    ))
    
    cards.append(Card(
        name="Tower Guard of Minas Tirith",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=2,
        power=1,
        toughness=3,
        rarity="Common",
        rules_text="Sentinel: While at a location you control, that location gains +1 Defense.",
        creature_types=["Man", "Soldier"],
        keywords=[Keyword.SENTINEL],
    ))
    
    cards.append(Card(
        name="Knight of Dol Amroth",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=3,
        power=3,
        toughness=3,
        rarity="Common",
        rules_text="Swan-knight's Valor: When attacking alongside another ally at same location, +1 Power.",
        creature_types=["Man", "Knight"],
    ))
    
    cards.append(Card(
        name="Ranger of Ithilien",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=3,
        power=2,
        toughness=3,
        rarity="Uncommon",
        rules_text="Ambush: May enter directly at contested location.\nScout: On enter, peek at top card of deck.",
        creature_types=["Man", "Ranger"],
        keywords=[Keyword.AMBUSH, Keyword.SCOUT],
    ))
    
    cards.append(Card(
        name="Citadel Healer",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=4,
        power=1,
        toughness=3,
        rarity="Uncommon",
        rules_text="Houses of Healing: Exhaust to heal 2 damage from target ally at same location (once/turn).",
        creature_types=["Man", "Healer"],
    ))
    
    cards.append(Card(
        name="Guard of the Fountain Court",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=5,
        power=3,
        toughness=5,
        rarity="Common",
        rules_text="Fortify: +1 Defense to location on enter.\nSteadfast: Cannot be moved by enemy effects.",
        creature_types=["Man", "Soldier"],
        keywords=[Keyword.FORTIFY, Keyword.STEADFAST],
    ))
    
    cards.append(Card(
        name="Imrahil, Prince of Dol Amroth",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=6,
        power=4,
        toughness=6,
        rarity="Rare",
        rules_text="Rally the Swan-knights: On enter, heal 1 from each other Gondor ally.\n"
                   "Valour: +1 Power while at contested location.",
        creature_types=["Man", "Knight", "Noble"],
        keywords=[Keyword.VALOUR],
    ))
    
    # Filler allies
    cards.append(Card(
        name="Gondor Spearman",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=2,
        power=2,
        toughness=2,
        rarity="Common",
        rules_text="A stalwart defender of the White City.",
        creature_types=["Man", "Soldier"],
    ))
    
    cards.append(Card(
        name="Minas Tirith Guard",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=1,
        power=1,
        toughness=2,
        rarity="Common",
        rules_text="First line of defense for the City of Kings.",
        creature_types=["Man", "Soldier"],
    ))
    
    cards.append(Card(
        name="Gondor Archer",
        faction=Faction.GONDOR,
        card_type=CardType.ALLY,
        cost=3,
        power=2,
        toughness=2,
        rarity="Common",
        rules_text="Ranged: Can attack from the back line.",
        creature_types=["Man", "Archer"],
        keywords=[Keyword.RANGED],
    ))
    
    # Events
    cards.append(Card(
        name="The Beacons Are Lit",
        faction=Faction.GONDOR,
        card_type=CardType.EVENT,
        cost=2,
        rarity="Common",
        rules_text="Search top 5 cards for a Gondor ally, reveal it, and put it into your hand.",
    ))
    
    cards.append(Card(
        name="For Gondor!",
        faction=Faction.GONDOR,
        card_type=CardType.EVENT,
        cost=5,
        rarity="Uncommon",
        rules_text="All Gondor allies at target location gain +2 Toughness until end of turn.",
    ))
    
    cards.append(Card(
        name="The Last Debate",
        faction=Faction.GONDOR,
        card_type=CardType.EVENT,
        cost=4,
        rarity="Rare",
        rules_text="Look at top 7 cards. Reveal one and add to hand. Put rest on bottom.",
    ))
    
    # Artifacts
    cards.append(Card(
        name="Andúril, Flame of the West",
        faction=Faction.GONDOR,
        card_type=CardType.ARTIFACT,
        cost=6,
        rarity="Legendary",
        rules_text="Attach to Gondor Hero. Bearer gains +3 Power.\n"
                   "Flame of the West: Exhaust to deal 3 damage to Nazgûl/Orc at same location.",
    ))
    
    cards.append(Card(
        name="The Horn of Gondor",
        faction=Faction.GONDOR,
        card_type=CardType.ARTIFACT,
        cost=4,
        rarity="Rare",
        rules_text="Attach to Gondor ally.\n"
                   "Once per game: Sacrifice; all Gondor allies gain +2 Power and Charge.",
    ))
    
    # Location
    cards.append(Card(
        name="Minas Tirith",
        faction=Faction.GONDOR,
        card_type=CardType.LOCATION,
        cost=4,
        defense=5,
        rarity="Rare",
        rules_text="Gondor allies at this location have +1 Toughness.\n"
                   "When flipped: Draw 2 cards.",
    ))
    
    return cards


# Pre-constructed 30-card Gondor deck
GONDOR_DECK = [
    # 3x Watchman of Minas Tirith (1-cost)
    Card(name="Watchman of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="Vigilant: +1 Defense on enter."),
    Card(name="Watchman of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="Vigilant: +1 Defense on enter."),
    Card(name="Watchman of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="Vigilant: +1 Defense on enter."),
    
    # 3x Minas Tirith Guard (1-cost filler)
    Card(name="Minas Tirith Guard", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="First line of defense."),
    Card(name="Minas Tirith Guard", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="First line of defense."),
    Card(name="Minas Tirith Guard", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=1, power=1, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="First line of defense."),
    
    # 3x Tower Guard (2-cost)
    Card(name="Tower Guard of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Man", "Soldier"],
         rules_text="Sentinel: Location gains +1 Defense.", keywords=[Keyword.SENTINEL]),
    Card(name="Tower Guard of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Man", "Soldier"],
         rules_text="Sentinel: Location gains +1 Defense.", keywords=[Keyword.SENTINEL]),
    Card(name="Tower Guard of Minas Tirith", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=1, toughness=3, creature_types=["Man", "Soldier"],
         rules_text="Sentinel: Location gains +1 Defense.", keywords=[Keyword.SENTINEL]),
    
    # 3x Gondor Spearman (2-cost filler)
    Card(name="Gondor Spearman", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="A stalwart defender."),
    Card(name="Gondor Spearman", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="A stalwart defender."),
    Card(name="Gondor Spearman", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=2, power=2, toughness=2, creature_types=["Man", "Soldier"],
         rules_text="A stalwart defender."),
    
    # 2x Knight of Dol Amroth (3-cost)
    Card(name="Knight of Dol Amroth", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Man", "Knight"],
         rules_text="Valor: +1 Power when attacking alongside another ally."),
    Card(name="Knight of Dol Amroth", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=3, toughness=3, creature_types=["Man", "Knight"],
         rules_text="Valor: +1 Power when attacking alongside another ally."),
    
    # 2x Ranger of Ithilien (3-cost)
    Card(name="Ranger of Ithilien", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=3, creature_types=["Man", "Ranger"],
         rules_text="Ambush, Scout.", keywords=[Keyword.AMBUSH, Keyword.SCOUT]),
    Card(name="Ranger of Ithilien", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=3, creature_types=["Man", "Ranger"],
         rules_text="Ambush, Scout.", keywords=[Keyword.AMBUSH, Keyword.SCOUT]),
    
    # 2x Gondor Archer (3-cost)
    Card(name="Gondor Archer", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=2, creature_types=["Man", "Archer"],
         rules_text="Ranged.", keywords=[Keyword.RANGED]),
    Card(name="Gondor Archer", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=3, power=2, toughness=2, creature_types=["Man", "Archer"],
         rules_text="Ranged.", keywords=[Keyword.RANGED]),
    
    # 2x Citadel Healer (4-cost)
    Card(name="Citadel Healer", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=4, power=1, toughness=3, creature_types=["Man", "Healer"],
         rules_text="Houses of Healing: Exhaust to heal 2 damage (once/turn)."),
    Card(name="Citadel Healer", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=4, power=1, toughness=3, creature_types=["Man", "Healer"],
         rules_text="Houses of Healing: Exhaust to heal 2 damage (once/turn)."),
    
    # 1x Guard of the Fountain Court (5-cost)
    Card(name="Guard of the Fountain Court", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=5, power=3, toughness=5, creature_types=["Man", "Soldier"],
         rules_text="Fortify +1, Steadfast.", keywords=[Keyword.FORTIFY, Keyword.STEADFAST]),
    
    # 1x Imrahil (6-cost)
    Card(name="Imrahil, Prince of Dol Amroth", faction=Faction.GONDOR, card_type=CardType.ALLY,
         cost=6, power=4, toughness=6, creature_types=["Man", "Knight", "Noble"],
         rules_text="Rally on enter, Valour.", keywords=[Keyword.VALOUR]),
    
    # Events
    Card(name="The Beacons Are Lit", faction=Faction.GONDOR, card_type=CardType.EVENT,
         cost=2, rules_text="Search top 5 for a Gondor ally."),
    Card(name="The Beacons Are Lit", faction=Faction.GONDOR, card_type=CardType.EVENT,
         cost=2, rules_text="Search top 5 for a Gondor ally."),
    Card(name="For Gondor!", faction=Faction.GONDOR, card_type=CardType.EVENT,
         cost=5, rules_text="+2 Toughness to all Gondor allies at location."),
    Card(name="The Last Debate", faction=Faction.GONDOR, card_type=CardType.EVENT,
         cost=4, rules_text="Look at top 7, pick one."),
    
    # Artifacts
    Card(name="Andúril, Flame of the West", faction=Faction.GONDOR, card_type=CardType.ARTIFACT,
         cost=6, rules_text="+3 Power. Exhaust to deal 3 damage to Orc/Nazgûl."),
    Card(name="The Horn of Gondor", faction=Faction.GONDOR, card_type=CardType.ARTIFACT,
         cost=4, rules_text="Sacrifice: +2 Power and Charge to all Gondor allies."),
    
    # Locations
    Card(name="Minas Tirith", faction=Faction.GONDOR, card_type=CardType.LOCATION,
         cost=4, defense=5, rules_text="Gondor allies here have +1 Toughness."),
    Card(name="Minas Tirith", faction=Faction.GONDOR, card_type=CardType.LOCATION,
         cost=4, defense=5, rules_text="Gondor allies here have +1 Toughness."),
]
