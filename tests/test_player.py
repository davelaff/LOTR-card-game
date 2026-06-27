"""
Unit tests for PlayerState — willpower, fatigue, deck management.
"""
import pytest
from engine.card import Card, CardType, Faction
from engine.player import PlayerState


def make_player(fp=True):
    """Factory for a PlayerState with optional deck setup."""
    return PlayerState(
        name="Test Player",
        faction=Faction.GONDOR,
        is_free_peoples=fp,
    )


def make_card(name="Test Card", cost=1):
    return Card(
        name=name, faction=Faction.GONDOR, card_type=CardType.ALLY,
        cost=cost, power=1, toughness=1,
    )


class TestWillpower:
    """Willpower pool and spending."""

    def test_initial_willpower_zero(self):
        player = make_player()
        assert player.willpower_pool == 0
        assert player.willpower_max == 1

    def test_spend_willpower_succeeds_when_enough(self):
        player = make_player()
        player.willpower_pool = 5
        assert player.spend_willpower(3)
        assert player.willpower_pool == 2

    def test_spend_willpower_fails_when_insufficient(self):
        player = make_player()
        player.willpower_pool = 2
        assert not player.spend_willpower(5)
        assert player.willpower_pool == 2  # Unchanged on failure

    def test_add_willpower_can_exceed_max(self):
        player = make_player()
        player.willpower_max = 3
        player.willpower_pool = 3
        player.add_willpower(2)
        assert player.willpower_pool == 5  # Can exceed cap

    def test_effective_willpower_max_normal(self):
        player = make_player()
        player.willpower_max = 5
        assert player.effective_willpower_max == 5

    def test_effective_willpower_max_leaderless_penalty(self):
        player = make_player()
        player.willpower_max = 5
        player.leaderless = True
        assert player.effective_willpower_max == 3  # 5 - 2

    def test_leaderless_penalty_floor_is_1(self):
        player = make_player()
        player.willpower_max = 2
        player.leaderless = True
        assert player.effective_willpower_max == 1  # max(1, 2-2)


class TestDeckDrawing:
    """Drawing from deck."""

    def test_draw_card_from_deck(self):
        player = make_player()
        card1 = make_card("Card A")
        card2 = make_card("Card B")
        player.deck = [card1, card2]
        drawn = player.draw_card()
        assert drawn is card2  # Drawn from end (top of deck)
        assert len(player.deck) == 1
        assert len(player.hand) == 1

    def test_draw_cards_multiple(self):
        player = make_player()
        player.deck = [make_card(f"Card {i}") for i in range(5)]
        drawn = player.draw_cards(3)
        assert len(drawn) == 3
        assert len(player.deck) == 2
        assert len(player.hand) == 3

    def test_draw_from_empty_deck_triggers_fatigue(self):
        player = make_player()
        player.influence = 30
        player.deck = []
        result = player.draw_card()
        assert result is None
        assert player.fatigue_counter == 1
        assert player.influence == 29  # Lost fatigue_counter (1) influence

    def test_fatigue_damage_escalates(self):
        """Each fatigue draw deals more influence damage."""
        player = make_player()
        player.influence = 30
        player.deck = []
        # First fatigue: lose 1
        player.draw_card()
        assert player.influence == 29
        # Second fatigue: lose 2
        player.draw_card()
        assert player.influence == 27
        # Third fatigue: lose 3
        player.draw_card()
        assert player.influence == 24

    def test_shuffle_deck(self):
        player = make_player()
        player.deck = [make_card(f"Card {i}") for i in range(10)]
        original_order = [c.name for c in player.deck]
        player.shuffle_deck()
        new_order = [c.name for c in player.deck]
        # With 10 cards, odds of same order are 1/10! — effectively impossible
        assert set(new_order) == set(original_order)  # Same cards
        # Don't assert order changed (could theoretically stay same)


class TestHandManagement:
    """Playing and discarding from hand."""

    def test_play_card_removes_from_hand(self):
        player = make_player()
        card = make_card()
        player.hand = [card]
        assert player.play_card(card)
        assert len(player.hand) == 0

    def test_play_card_not_in_hand_returns_false(self):
        player = make_player()
        card = make_card()
        player.hand = []
        assert not player.play_card(card)

    def test_play_card_by_instance_id(self):
        """Cards are matched by instance_id, not object identity."""
        player = make_player()
        card = make_card()
        clone = Card(
            name=card.name, faction=card.faction, card_type=card.card_type,
            cost=card.cost, power=card.power, toughness=card.toughness,
            instance_id=card.instance_id,
        )
        player.hand = [card]
        assert player.play_card(clone)  # Same instance_id


class TestInfluence:
    """Influence damage and defeat."""

    def test_initial_influence_is_30(self):
        player = make_player()
        assert player.influence == 30

    def test_deal_influence_damage(self):
        player = make_player()
        player.deal_influence_damage(5)
        assert player.influence == 25

    def test_influence_floor_is_zero(self):
        player = make_player()
        player.deal_influence_damage(100)
        assert player.influence == 0

    def test_is_defeated_at_zero(self):
        player = make_player()
        player.influence = 0
        assert player.is_defeated()

    def test_is_not_defeated_at_one(self):
        player = make_player()
        player.influence = 1
        assert not player.is_defeated()
