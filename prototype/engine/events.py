"""
Event card resolution — per-card handler functions with a dispatch registry.

Each handler: (game, player_state, enemy_state, player, enemy) -> list of messages.
player is "fp" or "shadow". enemy is the opposite.
"""
from engine.card import Card, CardType, Faction, Keyword, BoardAlly
from engine.effects import create_orc_token, create_rider_token, create_goblin_token, create_uruk_hai_token


# ---------------------------------------------------------------------------
# Gondor events
# ---------------------------------------------------------------------------

def _beacons_are_lit(game, ps, es, player, enemy):
    msgs = []
    deck = ps.deck
    search_count = min(5, len(deck))
    found = None
    searched = []
    for _ in range(search_count):
        c = deck.pop()
        if c.card_type == CardType.ALLY and c.faction == Faction.GONDOR and not found:
            found = c
        else:
            searched.append(c)
    if found:
        ps.hand.append(found)
        msgs.append(f"Found {found.name}! Added to hand.")
    deck.extend(searched)
    ps.shuffle_deck()
    msgs.append(f"Searched {search_count} cards.")
    return msgs


def _for_gondor(game, ps, es, player, enemy):
    msgs = []
    count = 0
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            ally.toughness_bonus += 2
            count += 1
    msgs.append(f"For Gondor! {count} allies gain +2 Toughness this turn.")
    return msgs


def _last_debate(game, ps, es, player, enemy):
    msgs = []
    search_count = min(7, len(ps.deck))
    msgs.append(f"Looked at top {search_count} cards. (Simplified: draw 1)")
    ps.draw_card()
    return msgs


# ---------------------------------------------------------------------------
# Mordor events
# ---------------------------------------------------------------------------

def _shadow_spreads(game, ps, es, player, enemy):
    msgs = []
    game.ring.add_corruption(1)
    msgs.append(f"Shadow Spreads: +1 Corruption (now {game.ring.corruption}/30).")
    for loc in game.board.locations:
        if loc.controller == player or loc.is_contested():
            token = create_orc_token()
            token_ally = BoardAlly(
                card=token, current_toughness=token.toughness,
                turn_entered=ps.turn_number,
            )
            loc.add_ally(token_ally, player, "front")
            msgs.append(f"Created Orc Token at {loc.location_card.name if loc.location_card else 'Open Field'}.")
            break
    return msgs


def _shadows_reach(game, ps, es, player, enemy):
    msgs = []
    es.deal_influence_damage(2)
    game.ring.add_corruption(1)
    msgs.append(f"Shadow's Reach: 2 Burn damage to {'Free Peoples' if enemy == 'fp' else 'Shadow'} Influence!")
    msgs.append(f"+1 Corruption (now {game.ring.corruption}/30).")
    return msgs


def _lidless_eye(game, ps, es, player, enemy):
    msgs = []
    game.ring.add_corruption(1)
    msgs.append(f"Lidless Eye: +1 Corruption (now {game.ring.corruption}/30).")
    if es.hand:
        discarded = es.hand.pop()
        es.discard.append(discarded)
        msgs.append(f"Opponent discards {discarded.name}.")
    return msgs


def _fires_of_mount_doom(game, ps, es, player, enemy):
    msgs = []
    game.ring.add_corruption(2)
    for loc in game.board.locations:
        for ally in loc.get_allies(enemy):
            ally.take_damage(3)
    msgs.append("Fires of Mount Doom: 3 damage to all enemies! +2 Corruption.")
    return msgs


# ---------------------------------------------------------------------------
# Elven events
# ---------------------------------------------------------------------------

def _lembas(game, ps, es, player, enemy):
    msgs = []
    hero = ps.hero
    if hero and hero.damage > 0:
        healed = hero.heal(3)
        msgs.append(f"Lembas: Healed {healed} damage from {hero.card.name} (+1 Power this turn).")
    else:
        msgs.append("Lembas: No damage to heal. (+1 Power still gained.)")
    return msgs


def _last_alliance(game, ps, es, player, enemy):
    msgs = []
    count = min(8, len(ps.deck))
    msgs.append(f"The Last Alliance: Revealed top {count}. (Simplified: draw 2)")
    ps.draw_cards(2)
    return msgs


def _light_of_the_evenstar(game, ps, es, player, enemy):
    msgs = []
    target = None
    hero = ps.hero
    if hero and hero.is_alive:
        target = hero
    else:
        all_allies = game.board.get_all_allies(player)
        if all_allies:
            target = max(all_allies, key=lambda a: a.card.power)
    if target:
        target.add_temp_keyword(Keyword.STEALTH)
        target.power_bonus += 1
        target.toughness_bonus += 1
        msgs.append(f"Light of the Evenstar: {target.card.name} gains Stealth and +1/+1 this turn.")
    else:
        msgs.append("Light of the Evenstar: No valid target.")
    return msgs


# ---------------------------------------------------------------------------
# Dwarven events
# ---------------------------------------------------------------------------

def _to_me_o_my_kinsfolk(game, ps, es, player, enemy):
    msgs = []
    count = min(5, len(ps.deck))
    msgs.append(f"To Me! O My Kinsfolk!: Revealed top {count}. (Simplified: draw 1)")
    ps.draw_card()
    return msgs


def _ire_of_the_mountain(game, ps, es, player, enemy):
    msgs = []
    destroyed = False
    for loc in game.board.locations:
        if loc.controller == enemy and loc.location_card and loc.current_defense > 0:
            loc_name = loc.location_card.name
            loc.location_card = None
            loc.current_defense = 0
            loc.controller = None
            loc.fortify_bonus = 0
            msgs.append(f"The Ire of the Mountain: Destroyed {loc_name}!")
            destroyed = True
            break
        for ally in loc.get_allies(enemy):
            if ally.artifacts:
                art = ally.artifacts.pop(0)
                es.discard.append(art)
                msgs.append(f"The Ire of the Mountain: Destroyed {art.name}!")
                destroyed = True
                break
        if destroyed:
            break
    if not destroyed:
        msgs.append("The Ire of the Mountain: No enemy Artifact or Location to destroy.")
    has_dwarf = False
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if "Dwarf" in ally.card.creature_types:
                has_dwarf = True
                break
    if has_dwarf:
        drawn = ps.draw_cards(2)
        msgs.append(f"Controlling a Dwarf: Drew {len(drawn)} cards.")
    return msgs


def _hammer_falls(game, ps, es, player, enemy):
    msgs = []
    target_loc = game.board.get_location(1)
    for ally in target_loc.get_allies(enemy):
        ally.take_damage(4)
    msgs.append("The Hammer Falls: 4 damage to enemies at center location!")
    return msgs


# ---------------------------------------------------------------------------
# Rohan events
# ---------------------------------------------------------------------------

def _ride_of_the_rohirrim(game, ps, es, player, enemy):
    msgs = []
    target = None
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if ally.card.faction == Faction.ROHAN or "Rider" in ally.card.creature_types:
                if target is None or ally.card.power > target.card.power:
                    target = ally
    if ps.hero and ps.hero.card.faction == Faction.ROHAN:
        h = ps.hero
        if h.is_alive and (target is None or h.card.power > target.card.power):
            target = h
    if target:
        already_charge = target.has_charge
        target.add_temp_keyword(Keyword.CHARGE)
        bonus = 3 if already_charge else 2
        target.power_bonus += bonus
        msgs.append(f"Ride of the Rohirrim: {target.card.name} gains Charge and +{bonus} Power!")
    else:
        msgs.append("Ride of the Rohirrim: No Rohan ally to target.")
    return msgs


def _muster_the_rohirrim(game, ps, es, player, enemy):
    msgs = []
    deployed = 0
    controlled_locs = [loc for loc in game.board.locations
                       if loc.controller == player and not loc.is_empty()]
    for i in range(3):
        rider_card = create_rider_token()
        rider = BoardAlly(
            card=rider_card,
            current_toughness=rider_card.toughness,
            turn_entered=ps.turn_number,
            tapped=False,
        )
        if controlled_locs:
            target_loc = controlled_locs[i % len(controlled_locs)]
            target_loc.add_ally(rider, player, "front")
            deployed += 1
        else:
            game.board.deploy_ally(rider, player)
    msgs.append(f"Muster the Rohirrim: Created 3 Rider tokens (2/1 Charge)! {deployed} deployed to locations.")
    return msgs


def _forth_eorlingas(game, ps, es, player, enemy):
    msgs = []
    rohan_allies = []
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if ally.card.faction == Faction.ROHAN or "Rider" in ally.card.creature_types:
                rohan_allies.append(ally)
    rohan_allies.sort(key=lambda a: a.card.power, reverse=True)
    buffed = rohan_allies[:3]
    for ally in buffed:
        ally.add_temp_keyword(Keyword.CHARGE)
        ally.power_bonus += 2
        ally.take_damage(1)
    msgs.append(f"Forth Eorlingas! {len(buffed)} Rohan allies gain Charge and +2 Power (take 1 damage)!")
    return msgs


# ---------------------------------------------------------------------------
# Hobbit events
# ---------------------------------------------------------------------------

def _straight_road(game, ps, es, player, enemy):
    msgs = []
    msgs.append("The Straight Road: Ally gains Stealth. Draw a card if it survives.")
    ps.draw_card()
    return msgs


def _i_will_not_say(game, ps, es, player, enemy):
    msgs = []
    removed = min(3, game.ring.corruption)
    for _ in range(removed):
        if game.ring.corruption > 0:
            game.ring.corruption -= 1
    drawn = ps.draw_cards(removed)
    msgs.append(f"I Will Not Say: Removed {removed} Corruption! Drew {len(drawn)} cards.")
    return msgs


# ---------------------------------------------------------------------------
# Isengard events
# ---------------------------------------------------------------------------

def _white_hand(game, ps, es, player, enemy):
    msgs = []
    target = None
    target_loc = None
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if "Uruk-hai" in ally.card.creature_types:
                if target is None or ally.card.power > target.card.power:
                    target = ally
                    target_loc = loc
    if target:
        target.power_bonus += 2
        target.toughness_bonus += 2
        msgs.append(f"The White Hand: {target.card.name} gains +2/+2!")
        if target_loc and target_loc.is_contested():
            art_destroyed = False
            for enemy_ally in target_loc.get_allies(enemy):
                if enemy_ally.artifacts:
                    art = enemy_ally.artifacts.pop(0)
                    es.discard.append(art)
                    msgs.append(f"The White Hand: Destroyed {art.name} at contested location!")
                    art_destroyed = True
                    break
            if not art_destroyed:
                msgs.append("The White Hand: Contested, but no enemy Artifact to destroy.")
    else:
        msgs.append("The White Hand: No Uruk-hai ally to target.")
    return msgs


def _isengard_unleashed(game, ps, es, player, enemy):
    msgs = []
    reveal_count = min(6, len(ps.deck))
    put_in_play = []
    rest = []
    for _ in range(reveal_count):
        c = ps.deck.pop()
        if c.card_type == CardType.ALLY and "Uruk-hai" in c.creature_types:
            put_in_play.append(c)
        else:
            rest.append(c)
    for c in put_in_play:
        ally = BoardAlly(
            card=c, current_toughness=c.toughness,
            turn_entered=ps.turn_number, tapped=False,
        )
        target_loc_idx = -1
        for i, loc in enumerate(game.board.locations):
            if loc.controller == player or loc.is_contested():
                target_loc_idx = i
                break
        if target_loc_idx >= 0:
            game.board.get_location(target_loc_idx).add_ally(ally, player, "front")
        else:
            game.board.deploy_ally(ally, player)
    ps.deck = rest + ps.deck
    msgs.append(f"Isengard Unleashed: Revealed {reveal_count}, put {len(put_in_play)} Uruk-hai into play with Charge!")
    return msgs


def _new_power_rises(game, ps, es, player, enemy):
    msgs = []
    target_loc = None
    best_score = -1
    for loc in game.board.locations:
        score = len(loc.get_allies(player)) + len(loc.get_allies(enemy))
        if score > best_score:
            best_score = score
            target_loc = loc
    if target_loc is None:
        target_loc = game.board.get_location(1)
    artifacts_destroyed = 0
    for row_name in ["fp_front", "fp_back", "shadow_front", "shadow_back"]:
        row = getattr(target_loc, row_name, [])
        for ally in row:
            while ally.artifacts:
                art = ally.artifacts.pop()
                artifacts_destroyed += 1
                if row_name.startswith("fp"):
                    game.fp_player.discard.append(art)
                else:
                    game.shadow_player.discard.append(art)
    for _ in range(artifacts_destroyed):
        token_card = create_uruk_hai_token()
        token = BoardAlly(
            card=token_card, current_toughness=token_card.toughness,
            turn_entered=ps.turn_number,
        )
        target_loc.add_ally(token, player, "front")
    msgs.append(f"A New Power Rises: Destroyed {artifacts_destroyed} artifacts, created {artifacts_destroyed} 3/3 Uruk-hai tokens!")
    return msgs


# ---------------------------------------------------------------------------
# Moria events
# ---------------------------------------------------------------------------

def _drums_in_the_deep(game, ps, es, player, enemy):
    msgs = []
    returned = 0
    grab = []
    for c in list(ps.discard):
        if "Goblin" in c.creature_types and returned < 2:
            grab.append(c)
            returned += 1
    for c in grab:
        ps.discard.remove(c)
        ps.hand.append(c)
    token_card = create_goblin_token()
    token = BoardAlly(
        card=token_card, current_toughness=token_card.toughness,
        turn_entered=ps.turn_number,
    )
    placed = False
    for loc in game.board.locations:
        if loc.controller == player or loc.is_contested():
            loc.add_ally(token, player, "front")
            placed = True
            break
    if not placed:
        game.board.deploy_ally(token, player)
    msgs.append(f"Drums in the Deep: Returned {returned} Goblins from discard + created Goblin token!")
    return msgs


def _they_are_coming(game, ps, es, player, enemy):
    msgs = []
    goblins = []
    for c in list(ps.hand):
        if "Goblin" in c.creature_types and len(goblins) < 3:
            goblins.append(c)
    for c in goblins:
        ps.hand.remove(c)
        ally = BoardAlly(
            card=c, current_toughness=c.toughness,
            turn_entered=ps.turn_number, tapped=False,
        )
        placed = False
        for loc in game.board.locations:
            if loc.is_contested() or loc.controller == enemy:
                loc.add_ally(ally, player, "front")
                placed = True
                break
        if not placed:
            for loc in game.board.locations:
                if loc.controller == player:
                    loc.add_ally(ally, player, "front")
                    placed = True
                    break
        if not placed:
            game.board.deploy_ally(ally, player)
    msgs.append(f"They Are Coming: {len(goblins)} Goblins deployed via Ambush with Charge!")
    return msgs


def _chasm_opens(game, ps, es, player, enemy):
    msgs = []
    busiest = max(game.board.locations, key=lambda l: len(l.get_allies(enemy)))
    for ally in busiest.get_allies(enemy):
        ally.take_damage(2)
    msgs.append("The Chasm Opens: All Goblins relocated! 2 damage at busiest location!")
    return msgs


# ---------------------------------------------------------------------------
# Harad events
# ---------------------------------------------------------------------------

def _serpents_coil(game, ps, es, player, enemy):
    msgs = []
    target = None
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if (ally.card.faction == Faction.HARAD or
                any(t in ally.card.creature_types for t in ["Haradrim", "Easterling", "Mumak"])):
                if target is None or ally.card.power > target.card.power:
                    target = ally
    if target:
        is_mumak = "Mumak" in target.card.creature_types
        if is_mumak:
            if Keyword.INTIMIDATE not in target.card.keywords:
                target.card.keywords.append(Keyword.INTIMIDATE)
            msgs.append(f"The Serpent's Coil: {target.card.name} gains Intimidate permanently!")
        else:
            target.add_temp_keyword(Keyword.INTIMIDATE)
            msgs.append(f"The Serpent's Coil: {target.card.name} gains Intimidate this turn.")
    else:
        msgs.append("The Serpent's Coil: No Haradrim ally to target.")
    return msgs


def _from_the_south_and_east(game, ps, es, player, enemy):
    msgs = []
    search_count = min(6, len(ps.deck))
    found = None
    rest = []
    for _ in range(search_count):
        c = ps.deck.pop()
        if not found and c.card_type == CardType.ALLY and c.faction == Faction.HARAD:
            found = c
        else:
            rest.append(c)
    ps.deck = rest + ps.deck
    if found:
        ally = BoardAlly(
            card=found, current_toughness=found.toughness,
            turn_entered=ps.turn_number, tapped=False,
        )
        for loc in game.board.locations:
            if loc.controller == player or loc.is_contested():
                loc.add_ally(ally, player, "front")
                break
        else:
            game.board.deploy_ally(ally, player)
        msgs.append(f"From the South and East: Found {found.name}, deployed with Charge!")
    else:
        msgs.append(f"From the South and East: No Harad ally in top {search_count}.")
    return msgs


def _war_beasts_rampage(game, ps, es, player, enemy):
    msgs = []
    target = None
    target_loc = None
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if "Mumak" in ally.card.creature_types:
                target = ally
                target_loc = loc
                break
    if target:
        target.power_bonus += 2
        msgs.append(f"The War-beasts Rampage: {target.card.name} gains +2 Power!")
        enemy_allies = target_loc.get_allies(enemy) if target_loc else []
        attacks = min(2, len(enemy_allies))
        for i in range(attacks):
            if i < len(enemy_allies):
                e = enemy_allies[i]
                if e.is_alive:
                    dmg = target.effective_power
                    e.take_damage(dmg)
                    msgs.append(f"  Mumak attacks {e.card.name} for {dmg} damage!")
                    if dmg > e.current_toughness + e.damage:
                        excess = dmg - (e.current_toughness + e.damage)
                        if excess > 0:
                            es.deal_influence_damage(excess)
                            msgs.append(f"  Rampage: {excess} excess damage to enemy Influence!")
        if attacks == 0 and target_loc:
            es.deal_influence_damage(target.effective_power)
            msgs.append(f"  Mumak rampages! {target.effective_power} damage to enemy Influence!")
    else:
        msgs.append("The War-beasts Rampage: No Mumak to target.")
    return msgs


# ---------------------------------------------------------------------------
# Nazgul events
# ---------------------------------------------------------------------------

def _all_shall_fade(game, ps, es, player, enemy):
    msgs = []
    target = None
    target_loc = None
    for loc in game.board.locations:
        for ally in loc.get_allies(player):
            if ally.card.faction == Faction.NAZGUL or "Nazgul" in ally.card.creature_types:
                if target is None or ally.card.power > target.card.power:
                    target = ally
                    target_loc = loc
    if target is None:
        for loc in game.board.locations:
            for ally in loc.get_allies(player):
                if target is None or ally.card.power > target.card.power:
                    target = ally
                    target_loc = loc
    if target:
        if Keyword.WRATH_FORM not in target.card.keywords:
            target.card.keywords.append(Keyword.WRATH_FORM)
        msgs.append(f"All Shall Fade: {target.card.name} gains Wraith Form!")
        is_nazgul = (target.card.faction == Faction.NAZGUL or
                     "Nazgul" in target.card.creature_types)
        if is_nazgul and target_loc:
            for enemy_ally in target_loc.get_allies(enemy):
                enemy_ally.take_damage(3)
            msgs.append(f"All Shall Fade: 3 damage to enemies at location!")
    else:
        msgs.append("All Shall Fade: No valid target.")
    return msgs


def _ring_is_mine(game, ps, es, player, enemy):
    msgs = []
    game.ring.add_corruption(1)
    msgs.append(f"The Ring Is Mine: +1 Corruption (now {game.ring.corruption}/30). FP may activate Ring or lose 3 Influence.")
    es.deal_influence_damage(3)
    msgs.append("Free Peoples lose 3 Influence from the Ring's call!")
    return msgs


# ---------------------------------------------------------------------------
# Dispatch registry
# ---------------------------------------------------------------------------

EVENT_HANDLERS = {
    # Gondor
    "The Beacons Are Lit": _beacons_are_lit,
    "For Gondor!": _for_gondor,
    "The Last Debate": _last_debate,
    # Mordor
    "The Shadow Spreads": _shadow_spreads,
    "Shadow's Reach": _shadows_reach,
    "The Lidless Eye": _lidless_eye,
    "The Fires of Mount Doom": _fires_of_mount_doom,
    # Elven
    "Lembas": _lembas,
    "The Last Alliance": _last_alliance,
    "The Light of the Evenstar": _light_of_the_evenstar,
    # Dwarven
    "To Me! O My Kinsfolk!": _to_me_o_my_kinsfolk,
    "The Ire of the Mountain": _ire_of_the_mountain,
    "The Hammer Falls": _hammer_falls,
    # Rohan
    "Ride of the Rohirrim": _ride_of_the_rohirrim,
    "Muster the Rohirrim": _muster_the_rohirrim,
    "Forth Eorlingas!": _forth_eorlingas,
    # Hobbit
    "The Straight Road": _straight_road,
    "I Will Not Say the Day Is Done": _i_will_not_say,
    # Isengard
    "The White Hand": _white_hand,
    "Isengard Unleashed": _isengard_unleashed,
    "A New Power Rises": _new_power_rises,
    # Moria
    "Drums in the Deep": _drums_in_the_deep,
    "They Are Coming": _they_are_coming,
    "The Chasm Opens": _chasm_opens,
    # Harad
    "The Serpent's Coil": _serpents_coil,
    "From the South and East": _from_the_south_and_east,
    "The War-beasts Rampage": _war_beasts_rampage,
    # Nazgul
    "All Shall Fade": _all_shall_fade,
    "The Ring Is Mine": _ring_is_mine,
}


def resolve_event(game, card, player):
    """Dispatch an event card to its handler. Returns list of messages."""
    player_state = game.fp_player if player == "fp" else game.shadow_player
    enemy_state = game.shadow_player if player == "fp" else game.fp_player
    enemy = "shadow" if player == "fp" else "fp"

    handler = EVENT_HANDLERS.get(card.name)
    if handler:
        return handler(game, player_state, enemy_state, player, enemy)
    return [f"{card.name} resolved (generic event)."]
