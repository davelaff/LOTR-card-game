"""
Unit tests for CombatResolver — damage, Trample, Fear, location attacks.
"""
import pytest
from engine.card import Card, CardType, Faction, Keyword, BoardAlly
from engine.board import Board, LocationSlot
from engine.game import GameState
from engine.player import PlayerState


def make_ally(name="Test Ally", power=2, toughness=3, keywords=None, turn_entered=1):
    card = Card(
        name=name, faction=Faction.GONDOR, card_type=CardType.ALLY,
        cost=2, power=power, toughness=toughness,
        keywords=keywords or [],
    )
    return BoardAlly(card=card, current_toughness=toughness, turn_entered=turn_entered)


def setup_game():
    """Minimal GameState for combat testing."""
    game = GameState()
    game.fp_player = PlayerState(
        name="Free Peoples", faction=Faction.GONDOR, is_free_peoples=True,
        influence=30, turn_number=2,
    )
    game.shadow_player = PlayerState(
        name="Shadow", faction=Faction.MORDOR, is_free_peoples=False,
        influence=30, turn_number=2,
    )
    game.board = Board()
    return game


def place_allies_at_location(game, attacker, defender=None, attacker_player="fp", loc_idx=1):
    """Place attacker and optional defender at a location."""
    game.board.deploy_ally(attacker, attacker_player)
    game.board.move_ally_to_location(attacker, attacker_player, loc_idx, "front")
    if defender:
        def_player = "shadow" if attacker_player == "fp" else "fp"
        game.board.deploy_ally(defender, def_player)
        game.board.move_ally_to_location(defender, def_player, loc_idx, "front")


class TestBasicCombat:
    """Basic attack resolution — damage, tapping, destruction."""

    def test_attack_deals_power_as_damage(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=3)
        defender = make_ally("Defender", toughness=4)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["damage_dealt"] == 3
        assert defender.damage == 3
        assert defender.current_toughness == 1

    def test_attack_taps_attacker(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=2)
        defender = make_ally("Defender", toughness=4)
        place_allies_at_location(game, attacker, defender)
        
        game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert attacker.tapped
        assert attacker.has_attacked_this_turn

    def test_attack_destroys_weaker_ally(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=5)
        defender = make_ally("Defender", toughness=2)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["target_destroyed"]
        assert defender.current_toughness == 0
        assert not defender.is_alive

    def test_attack_does_not_destroy_tougher_ally(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=1)
        defender = make_ally("Defender", toughness=5)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert not result["target_destroyed"]
        assert defender.is_alive


class TestBrutalKeyword:
    """Brutal: +1 damage."""

    def test_brutal_adds_one_damage(self):
        game = setup_game()
        attacker = make_ally("Brute", power=2, keywords=[Keyword.BRUTAL])
        defender = make_ally("Defender", toughness=4)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["damage_dealt"] == 3  # 2 + 1 Brutal
        assert defender.damage == 3


class TestTrampleKeyword:
    """Trample: excess damage hits Influence."""

    def test_trample_excess_damage_to_influence(self):
        game = setup_game()
        attacker = make_ally("Trampler", power=5, keywords=[Keyword.TRAMPLE])
        defender = make_ally("Defender", toughness=2)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["target_destroyed"]
        assert result["trample_damage"] == 3  # 5 - 2 toughness
        assert game.shadow_player.influence < 30  # Took trample damage

    def test_trample_with_no_excess(self):
        game = setup_game()
        attacker = make_ally("Trampler", power=2, keywords=[Keyword.TRAMPLE])
        defender = make_ally("Defender", toughness=3)
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["trample_damage"] == 0
        assert game.shadow_player.influence == 30  # No trample damage


class TestFearKeyword:
    """Fear keyword reduces attacker power."""

    def test_fear_reduces_incoming_damage(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=3)
        defender = make_ally("Scary Defender", toughness=4, keywords=[Keyword.FEAR])
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        # Each Fear reduces damage by 1 (simplified in combat.py)
        assert result["damage_dealt"] == 2  # 3 - 1 Fear
        assert defender.damage == 2

    def test_fear_minimum_damage_zero(self):
        game = setup_game()
        attacker = make_ally("Weakling", power=1)
        defender = make_ally("Very Scary", toughness=5, keywords=[Keyword.FEAR])
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["damage_dealt"] >= 0  # Capped at 0
        assert defender.damage == 0

    def test_temp_fear_also_works(self):
        """Fear granted temporarily (via add_temp_keyword) should also reduce damage."""
        game = setup_game()
        attacker = make_ally("Attacker", power=3)
        defender = make_ally("Scary Defender", toughness=4)
        defender.add_temp_keyword(Keyword.FEAR)  # Temporary Fear
        place_allies_at_location(game, attacker, defender)
        
        result = game.combat.resolve_attack(attacker, "fp", defender, "ally_front")
        assert result["damage_dealt"] == 2  # 3 - 1 (temp Fear)


class TestLocationAttack:
    """Attacking locations — defended vs undefended."""

    def test_undefended_location_hits_influence(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=4)
        # Place attacker at a location with no shadow defenders
        game.board.deploy_ally(attacker, "fp")
        game.board.move_ally_to_location(attacker, "fp", 1)
        # Center has Open Field — attack the location directly
        loc = game.board.locations[1]
        
        result = game.combat.resolve_attack(attacker, "fp", loc, "location")
        assert result["damage_dealt"] == 4
        assert game.shadow_player.influence == 26  # 30 - 4

    def test_defended_location_damages_defense(self):
        game = setup_game()
        attacker = make_ally("Attacker", power=3)
        defender = make_ally("Guard", toughness=3)
        place_allies_at_location(game, attacker, defender, "fp", 0)
        # Play a shadow-controlled location at slot 0
        from engine.card import Card, CardType, Faction as F
        loc_card = Card(name="Shadow Fort", faction=F.MORDOR, card_type=CardType.LOCATION,
                        cost=3, defense=5)
        game.board.play_location(loc_card, "shadow", 0)
        # Move everyone to slot 0 where the location is
        game.board.move_ally_to_location(attacker, "fp", 0)
        game.board.move_ally_to_location(defender, "shadow", 0)
        
        loc = game.board.locations[0]
        result = game.combat.resolve_attack(attacker, "fp", loc, "location")
        # Defended — goes to location defense, not influence
        assert result["damage_dealt"] == 3
        assert loc.current_defense == 2  # 5 - 3
        assert game.shadow_player.influence == 30  # Unchanged
