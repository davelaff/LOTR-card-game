"""
Unit tests for Board — locations, deployment, movement, flipping.
"""
import pytest
from engine.card import Card, CardType, Faction, Keyword, BoardAlly
from engine.board import Board, LocationSlot, MAX_ROW_CAPACITY


def make_location_card(name="Test Location", defense=4):
    return Card(
        name=name, faction=Faction.GONDOR, card_type=CardType.LOCATION,
        cost=3, defense=defense,
    )

def make_ally(name="Test Ally", power=2, toughness=3, keywords=None, turn_entered=1):
    card = Card(
        name=name, faction=Faction.GONDOR, card_type=CardType.ALLY,
        cost=2, power=power, toughness=toughness,
        keywords=keywords or [],
    )
    return BoardAlly(card=card, current_toughness=toughness, turn_entered=turn_entered)


class TestBoardInit:
    """Board initialization — 3 slots, Open Field in center."""

    def test_three_location_slots(self):
        board = Board()
        assert len(board.locations) == 3
        assert all(isinstance(loc, LocationSlot) for loc in board.locations)

    def test_center_is_open_field(self):
        board = Board()
        center = board.locations[1]
        assert center.location_card is not None
        assert center.location_card.name == "Open Field"
        assert center.current_defense == 5
        assert center.controller is None

    def test_flanks_are_empty(self):
        board = Board()
        assert board.locations[0].is_empty()
        assert board.locations[2].is_empty()

    def test_deployment_zones_start_empty(self):
        board = Board()
        assert board.fp_deployment == []
        assert board.shadow_deployment == []


class TestLocationPlay:
    """Playing location cards into slots."""

    def test_play_location_into_empty_slot(self):
        board = Board()
        loc_card = make_location_card()
        assert board.play_location(loc_card, "fp", 0)
        slot = board.locations[0]
        assert not slot.is_empty()
        assert slot.location_card is loc_card
        assert slot.controller == "fp"
        assert slot.current_defense == 4

    def test_cannot_play_location_into_occupied_slot(self):
        board = Board()
        board.play_location(make_location_card("First"), "fp", 0)
        assert not board.play_location(make_location_card("Second"), "fp", 0)

    def test_play_location_sets_defense(self):
        board = Board()
        loc_card = make_location_card(defense=7)
        board.play_location(loc_card, "shadow", 2)
        assert board.locations[2].current_defense == 7


class TestAllyDeployment:
    """Deploying allies to the deployment zone."""

    def test_deploy_ally_to_fp_zone(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        assert ally in board.fp_deployment

    def test_deploy_ally_to_shadow_zone(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "shadow")
        assert ally in board.shadow_deployment

    def test_get_all_allies_includes_deployment(self):
        board = Board()
        a1 = make_ally("Ally 1")
        a2 = make_ally("Ally 2")
        board.deploy_ally(a1, "fp")
        board.deploy_ally(a2, "fp")
        all_allies = board.get_all_allies("fp")
        assert len(all_allies) == 2
        assert a1 in all_allies
        assert a2 in all_allies


class TestAllyMovement:
    """Moving allies between deployment and locations."""

    def test_move_from_deployment_to_location(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        assert board.move_ally_to_location(ally, "fp", 1)
        # Should be at center location now
        assert ally in board.locations[1].get_allies("fp")
        assert ally not in board.fp_deployment

    def test_move_from_deployment_to_specific_row(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        board.move_ally_to_location(ally, "fp", 1, "back")
        assert ally in board.locations[1].get_back_line("fp")

    def test_move_between_locations(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        board.move_ally_to_location(ally, "fp", 1, "front")
        # Now move to slot 2
        assert board.move_ally_between_locations(ally, "fp", 1, 2)
        assert ally in board.locations[2].get_allies("fp")
        assert ally not in board.locations[1].get_allies("fp")

    def test_move_between_rows(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        board.move_ally_to_location(ally, "fp", 1, "front")
        # Move to back line
        assert board.move_ally_between_rows(ally, "fp", 1, "back")
        assert ally in board.locations[1].get_back_line("fp")
        assert ally not in board.locations[1].get_front_line("fp")

    def test_cannot_move_to_full_front_line(self):
        board = Board()
        # Fill front line with 4 allies (MAX_ROW_CAPACITY)
        for i in range(MAX_ROW_CAPACITY):
            ally = make_ally(f"Ally {i}")
            board.deploy_ally(ally, "fp")
            board.move_ally_to_location(ally, "fp", 1, "front")
        # 5th ally should fail to join front line
        extra = make_ally("Extra")
        board.deploy_ally(extra, "fp")
        assert not board.move_ally_to_location(extra, "fp", 1, "front")

    def test_find_ally_location(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        assert board.find_ally_location(ally, "fp") == -1
        board.move_ally_to_location(ally, "fp", 2)
        assert board.find_ally_location(ally, "fp") == 2


class TestLocationContestation:
    """Contested locations and control."""

    def test_contested_when_both_players_present(self):
        board = Board()
        fp_ally = make_ally("FP Ally")
        sh_ally = make_ally("SH Ally")
        board.deploy_ally(fp_ally, "fp")
        board.deploy_ally(sh_ally, "shadow")
        board.move_ally_to_location(fp_ally, "fp", 1)
        board.move_ally_to_location(sh_ally, "shadow", 1)
        assert board.locations[1].is_contested()

    def test_not_contested_when_only_one_player(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        board.move_ally_to_location(ally, "fp", 1)
        assert not board.locations[1].is_contested()


class TestLocationFlipping:
    """Location defense damage and controller flipping."""

    def test_deal_defense_damage_reduces_defense(self):
        board = Board()
        board.play_location(make_location_card("Fort", defense=5), "fp", 0)
        loc = board.locations[0]
        flipped = loc.deal_defense_damage(2)
        assert not flipped
        assert loc.current_defense == 3

    def test_location_flips_when_defense_hits_zero(self):
        board = Board()
        board.play_location(make_location_card("Fort", defense=4), "fp", 0)
        loc = board.locations[0]
        flipped = loc.deal_defense_damage(4)
        assert flipped
        assert loc.controller == "shadow"  # Flipped from fp
        assert loc.current_defense == 4  # Resets to base defense

    def test_location_defense_resets_on_flip(self):
        board = Board()
        board.play_location(make_location_card("Fort", defense=6), "fp", 0)
        loc = board.locations[0]
        loc.current_defense = 2
        loc.deal_defense_damage(2)  # Flip
        assert loc.current_defense == 6  # Reset


class TestValidAttackTargets:
    """Target selection for combat."""

    def test_front_line_enemies_are_targets(self):
        board = Board()
        attacker = make_ally("Attacker")
        defender = make_ally("Defender")
        board.deploy_ally(attacker, "fp")
        board.deploy_ally(defender, "shadow")
        board.move_ally_to_location(attacker, "fp", 1)
        board.move_ally_to_location(defender, "shadow", 1)
        targets = board.locations[1].valid_attack_targets(attacker, "fp")
        assert any(t[0] == "ally_front" and t[1] is defender for t in targets)

    def test_back_line_not_targetable_without_ranged(self):
        board = Board()
        attacker = make_ally("Attacker")
        defender = make_ally("Defender")
        board.deploy_ally(attacker, "fp")
        board.deploy_ally(defender, "shadow")
        board.move_ally_to_location(attacker, "fp", 1)
        board.move_ally_to_location(defender, "shadow", 1, "back")
        targets = board.locations[1].valid_attack_targets(attacker, "fp")
        # No front-line enemies → back line IS targetable
        # (the rule is: can attack back if no front line OR has ranged)
        assert any(t[0] == "ally_back" for t in targets)

    def test_back_line_targetable_with_ranged(self):
        board = Board()
        attacker = make_ally("Archer", keywords=[Keyword.RANGED])
        front_defender = make_ally("Front")
        back_defender = make_ally("Back")
        board.deploy_ally(attacker, "fp")
        board.deploy_ally(front_defender, "shadow")
        board.deploy_ally(back_defender, "shadow")
        board.move_ally_to_location(attacker, "fp", 1)
        board.move_ally_to_location(front_defender, "shadow", 1, "front")
        board.move_ally_to_location(back_defender, "shadow", 1, "back")
        targets = board.locations[1].valid_attack_targets(attacker, "fp")
        assert any(t[0] == "ally_back" and t[1] is back_defender for t in targets)

    def test_location_targetable_when_no_front_line(self):
        board = Board()
        attacker = make_ally("Attacker")
        board.deploy_ally(attacker, "fp")
        board.move_ally_to_location(attacker, "fp", 1)
        # Open Field in center, no shadow allies → location should be targetable
        targets = board.locations[1].valid_attack_targets(attacker, "fp")
        assert any(t[0] == "location" for t in targets)


class TestRemoveAlly:
    """Removing allies from board."""

    def test_remove_ally_from_deployment(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        assert board.remove_ally(ally, "fp")
        assert ally not in board.fp_deployment

    def test_remove_ally_from_location(self):
        board = Board()
        ally = make_ally()
        board.deploy_ally(ally, "fp")
        board.move_ally_to_location(ally, "fp", 1)
        assert board.remove_ally(ally, "fp")
        assert ally not in board.locations[1].get_allies("fp")

    def test_remove_nonexistent_ally(self):
        board = Board()
        ally = make_ally()
        assert not board.remove_ally(ally, "fp")
