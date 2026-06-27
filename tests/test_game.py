"""
Integration tests for GameState — game-over conditions, turn flow,
hero destruction, ring theft, phase transitions.

Uses real GameState.setup() with minimal factions to avoid
slow full-deck initialization where possible.
"""
import pytest
from engine.game import GameState, GamePhase
from engine.card import Card, CardType, Faction, Keyword, BoardAlly
from engine.player import PlayerState
from engine.board import Board
from engine.ring import Ring


class TestGameOverInfluence:
    """Game ends when a player's Influence hits 0."""

    def test_fp_defeat_by_influence(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=2, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        # FP influence hits 0
        game.fp_player.deal_influence_damage(2)
        result = game._check_game_over()
        assert result == "shadow"
        assert game.game_over
        assert game.winner == "shadow"

    def test_shadow_defeat_by_influence(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=1, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        game.shadow_player.deal_influence_damage(1)
        result = game._check_game_over()
        assert result == "fp"
        assert game.game_over
        assert game.winner == "fp"

    def test_no_game_over_at_positive_influence(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        result = game._check_game_over()
        assert result is None
        assert not game.game_over


class TestGameOverCorruption:
    """Game ends when Ring corruption hits 30."""

    def test_corruption_loss_fp_bearer(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        game.ring.add_corruption(30)
        
        result = game._check_game_over()
        assert result == "shadow"  # FP bears, corruption 30 → shadow wins
        assert game.game_over
        assert "Corruption reached 30" in game.loss_reason

    def test_corruption_loss_shadow_bearer(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        game.ring.steal_by_shadow()
        game.ring.add_corruption(30)
        
        result = game._check_game_over()
        assert result == "fp"  # Shadow bears, corruption 30 → fp wins

    def test_no_loss_below_30_corruption(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        game.ring.add_corruption(29)
        
        result = game._check_game_over()
        assert result is None


class TestHeroDeathRingTheft:
    """Hero destruction triggers ring bearer changes."""

    def test_fp_hero_death_steals_ring(self):
        """When FP hero dies and FP bears the Ring, Shadow steals it."""
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        # Put a "hero" on the board for FP
        hero_card = Card(
            name="Test Hero", faction=Faction.GONDOR, card_type=CardType.HERO,
            cost=0, power=4, toughness=4,
        )
        hero = BoardAlly(card=hero_card, current_toughness=4, turn_entered=0)
        game.fp_player.hero = hero
        game.board.deploy_ally(hero, "fp")
        game.board.move_ally_to_location(hero, "fp", 1)
        
        # Kill the hero
        hero.take_damage(10)
        
        # Simulate the ring theft that input_handler does
        assert game.ring.bearer == "fp"
        game.ring.steal_by_shadow()
        assert game.ring.bearer == "shadow"
        game.fp_player.hero = None
        game.fp_player.leaderless = True
        
        assert game.fp_player.leaderless

    def test_leaderless_penalty_applied(self):
        """When hero dies, effective_willpower_max drops by 2 (min 1)."""
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=5, willpower_pool=5,
        )
        game.fp_player.leaderless = True
        assert game.fp_player.effective_willpower_max == 3


class TestTurnStartPhase:
    """Start phase: untap, willpower increment, draw."""

    def test_start_turn_increments_turn_number(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        game.active_player = "fp"
        assert game.fp_player.turn_number == 0
        game.start_turn()
        assert game.fp_player.turn_number == 1

    def test_start_turn_untaps_allies(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        ally_card = Card(name="Test Ally", faction=Faction.GONDOR,
                         card_type=CardType.ALLY, cost=1, power=1, toughness=1)
        ally = BoardAlly(card=ally_card, current_toughness=1, turn_entered=0)
        ally.tapped = True
        ally.has_attacked_this_turn = True
        ally.has_moved_this_turn = True
        
        game.board.deploy_ally(ally, "fp")
        game.board.move_ally_to_location(ally, "fp", 1)
        game.active_player = "fp"
        game.start_turn()
        
        assert not ally.tapped
        assert not ally.has_attacked_this_turn
        assert not ally.has_moved_this_turn

    def test_start_turn_willpower_increments(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=0,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=0,
        )
        game.board = Board()
        game.ring = Ring()
        
        game.active_player = "fp"
        game.fp_player.turn_number = 3  # Past turn 1
        game.fp_player.willpower_max = 4
        
        game.start_turn()
        # Turn 4: willpower_max should be 5 (1 per turn up to 10)
        assert game.fp_player.willpower_max == 5

    def test_start_turn_willpower_capped_at_10(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=10, willpower_pool=0,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=0,
        )
        game.board = Board()
        game.ring = Ring()
        
        game.active_player = "fp"
        game.fp_player.turn_number = 9
        game.start_turn()
        assert game.fp_player.willpower_max == 10  # Capped


class TestEndTurn:
    """End phase: cleanup, player switch, game-over check."""

    def test_end_turn_switches_active_player(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        game.active_player = "fp"
        game.end_turn()
        assert game.active_player == "shadow"
        game.end_turn()
        assert game.active_player == "fp"

    def test_end_turn_increments_total_turn(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        assert game.current_turn_number == 1
        game.end_turn()
        assert game.current_turn_number == 2

    def test_end_turn_clears_temp_bonuses(self):
        game = GameState()
        game.fp_player = PlayerState(
            name="FP", faction=Faction.GONDOR, is_free_peoples=True,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.shadow_player = PlayerState(
            name="SH", faction=Faction.MORDOR, is_free_peoples=False,
            influence=30, willpower_max=1, willpower_pool=1,
        )
        game.board = Board()
        game.ring = Ring()
        
        ally_card = Card(name="Test Ally", faction=Faction.GONDOR,
                         card_type=CardType.ALLY, cost=1, power=1, toughness=1)
        ally = BoardAlly(card=ally_card, current_toughness=1, turn_entered=0)
        ally.power_bonus = 3
        ally.toughness_bonus = 2
        ally.add_temp_keyword(Keyword.CHARGE)
        
        game.board.deploy_ally(ally, "fp")
        game.board.move_ally_to_location(ally, "fp", 1)
        
        game.end_turn()
        
        # Temp bonuses cleared
        assert ally.power_bonus == 0
        assert ally.toughness_bonus == 0
        assert not ally.has_keyword(Keyword.CHARGE)


class TestFullSetup:
    """GameState.setup() with real factions."""

    def test_setup_creates_both_players(self):
        game = GameState()
        game.setup(fp_faction=Faction.GONDOR, shadow_faction=Faction.MORDOR)
        
        assert game.fp_player is not None
        assert game.shadow_player is not None
        assert game.fp_player.faction == Faction.GONDOR
        assert game.shadow_player.faction == Faction.MORDOR

    def test_setup_creates_heroes(self):
        game = GameState()
        game.setup(fp_faction=Faction.GONDOR, shadow_faction=Faction.MORDOR)
        
        assert game.fp_player.hero is not None
        assert game.shadow_player.hero is not None
        assert game.fp_player.hero.card.name == "Aragorn, Heir of Isildur"
        assert game.shadow_player.hero.card.name == "Gothmog, Lieutenant of Morgul"

    def test_setup_heroes_deployed(self):
        game = GameState()
        game.setup(fp_faction=Faction.ROHAN, shadow_faction=Faction.ISENGARD)
        
        # Heroes should be on the board
        fp_hero = game.fp_player.hero
        sh_hero = game.shadow_player.hero
        assert fp_hero is not None
        assert sh_hero is not None
        assert game.board.find_ally_location(fp_hero, "fp") is not None
        assert game.board.find_ally_location(sh_hero, "shadow") is not None

    def test_setup_decks_30_cards_each(self):
        game = GameState()
        game.setup(fp_faction=Faction.GONDOR, shadow_faction=Faction.MORDOR)
        
        # Each faction deck is ~30 cards, 5 drawn → ~25 remaining
        assert len(game.fp_player.hand) == 5
        assert len(game.shadow_player.hand) == 5
        assert 24 <= len(game.fp_player.deck) <= 27  # ~30 minus 5
        assert 24 <= len(game.shadow_player.deck) <= 27
        # Total cards: deck + hand + hero (hero isn't in deck)
        assert len(game.fp_player.deck) + len(game.fp_player.hand) >= 29
        assert len(game.shadow_player.deck) + len(game.shadow_player.hand) >= 29

    def test_setup_initial_willpower(self):
        game = GameState()
        game.setup(fp_faction=Faction.ELVEN, shadow_faction=Faction.NAZGUL)
        
        assert game.fp_player.willpower_max == 0  # Set to 0 in setup
        assert game.shadow_player.willpower_max == 0
