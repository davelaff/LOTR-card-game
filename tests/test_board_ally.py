"""
Unit tests for BoardAlly — the card-on-board wrapper.
"""
import pytest
from engine.card import Card, CardType, Faction, Keyword, BoardAlly


def make_ally(name="Test Ally", power=2, toughness=3, keywords=None, turn_entered=1):
    """Factory for a standard BoardAlly in tests."""
    card = Card(
        name=name, faction=Faction.GONDOR, card_type=CardType.ALLY,
        cost=2, power=power, toughness=toughness,
        keywords=keywords or [],
    )
    return BoardAlly(card=card, current_toughness=toughness, turn_entered=turn_entered)


class TestCanAttack:
    """Summoning sickness and attack eligibility."""

    def test_cannot_attack_turn_entered(self):
        """Allies can't attack the turn they enter (summoning sickness)."""
        ally = make_ally(turn_entered=3)
        assert not ally.can_attack(current_turn=3)

    def test_charge_bypasses_summoning_sickness(self):
        """Charge keyword lets allies attack the turn they enter."""
        ally = make_ally(keywords=[Keyword.CHARGE], turn_entered=3)
        assert ally.can_attack(current_turn=3)

    def test_can_attack_next_turn(self):
        """Allies can attack starting the turn after they enter."""
        ally = make_ally(turn_entered=3)
        assert ally.can_attack(current_turn=4)

    def test_tapped_ally_cannot_attack(self):
        """Tapped allies cannot attack regardless of other conditions."""
        ally = make_ally(turn_entered=2, keywords=[Keyword.CHARGE])
        ally.tapped = True
        assert not ally.can_attack(current_turn=3)

    def test_already_attacked_cannot_attack_again(self):
        """An ally that has attacked this turn cannot attack again."""
        ally = make_ally(turn_entered=1)
        ally.has_attacked_this_turn = True
        assert not ally.can_attack(current_turn=3)

    def test_dead_ally_cannot_attack(self):
        """A destroyed ally (toughness <= 0) cannot attack."""
        ally = make_ally(turn_entered=1)
        ally.current_toughness = 0
        assert not ally.can_attack(current_turn=3)

    def test_charge_temp_keyword_works(self):
        """Charge granted temporarily (via add_temp_keyword) also bypasses sickness."""
        ally = make_ally(turn_entered=5)
        ally.add_temp_keyword(Keyword.CHARGE)
        assert ally.can_attack(current_turn=5)


class TestDamageAndHealing:
    """Persistent damage and healing."""

    def test_take_damage_reduces_toughness(self):
        ally = make_ally(toughness=3)
        ally.take_damage(2)
        assert ally.current_toughness == 1
        assert ally.damage == 2

    def test_take_damage_kills_ally(self):
        ally = make_ally(toughness=2)
        ally.take_damage(3)
        assert ally.current_toughness == 0
        assert not ally.is_alive

    def test_heal_restores_toughness(self):
        ally = make_ally(toughness=4)
        ally.take_damage(3)
        healed = ally.heal(2)
        assert healed == 2
        assert ally.current_toughness == 3
        assert ally.damage == 1

    def test_heal_cannot_exceed_max(self):
        """Healing can't go beyond the card's base toughness."""
        ally = make_ally(toughness=4)
        ally.take_damage(1)
        healed = ally.heal(5)
        assert healed == 1  # Only 1 damage to heal
        assert ally.current_toughness == 4
        assert ally.damage == 0


class TestKeywords:
    """Keyword checks — permanent, temporary, and property shortcuts."""

    def test_has_keyword_permanent(self):
        ally = make_ally(keywords=[Keyword.RANGED])
        assert ally.has_keyword(Keyword.RANGED)

    def test_has_keyword_temporary(self):
        ally = make_ally()
        ally.add_temp_keyword(Keyword.STEALTH)
        assert ally.has_keyword(Keyword.STEALTH)

    def test_has_keyword_false_for_absent(self):
        ally = make_ally(keywords=[Keyword.RANGED])
        assert not ally.has_keyword(Keyword.TRAMPLE)

    def test_clear_temp_bonuses_removes_temp_keywords(self):
        ally = make_ally()
        ally.add_temp_keyword(Keyword.CHARGE)
        ally.power_bonus = 3
        ally.toughness_bonus = 2
        ally.clear_temp_bonuses()
        assert not ally.has_keyword(Keyword.CHARGE)
        assert ally.power_bonus == 0
        assert ally.toughness_bonus == 0
        # Permanent keywords survive
        ally2 = make_ally(keywords=[Keyword.RANGED])
        ally2.add_temp_keyword(Keyword.CHARGE)
        ally2.clear_temp_bonuses()
        assert ally2.has_keyword(Keyword.RANGED)
        assert not ally2.has_keyword(Keyword.CHARGE)

    def test_has_charge_property(self):
        assert make_ally(keywords=[Keyword.CHARGE]).has_charge
        assert not make_ally().has_charge

    def test_has_ranged_property(self):
        assert make_ally(keywords=[Keyword.RANGED]).has_ranged
        assert not make_ally().has_ranged

    def test_has_trample_property(self):
        assert make_ally(keywords=[Keyword.TRAMPLE]).has_trample
        assert not make_ally().has_trample


class TestEffectiveStats:
    """effective_power and effective_toughness include bonuses."""

    def test_base_stats_no_bonuses(self):
        ally = make_ally(power=2, toughness=3)
        assert ally.effective_power == 2
        assert ally.effective_toughness == 3

    def test_bonuses_applied(self):
        ally = make_ally(power=2, toughness=3)
        ally.power_bonus = 2
        ally.toughness_bonus = 1
        assert ally.effective_power == 4
        assert ally.effective_toughness == 4

    def test_toughness_bonus_with_damage(self):
        """Toughness bonus adds to current_toughness, not card base."""
        ally = make_ally(toughness=3)
        ally.take_damage(2)
        ally.toughness_bonus = 1
        assert ally.effective_toughness == 2  # (3-2) + 1


class TestCanMove:
    """Movement eligibility."""

    def test_can_move_when_untapped(self):
        ally = make_ally(turn_entered=1)
        assert ally.can_move()

    def test_cannot_move_when_tapped(self):
        ally = make_ally()
        ally.tapped = True
        assert not ally.can_move()

    def test_cannot_move_after_moving(self):
        ally = make_ally()
        ally.has_moved_this_turn = True
        assert not ally.can_move()

    def test_cannot_move_after_attacking(self):
        ally = make_ally()
        ally.has_attacked_this_turn = True
        assert not ally.can_move()

    def test_dead_ally_cannot_move(self):
        ally = make_ally()
        ally.current_toughness = 0
        assert not ally.can_move()
