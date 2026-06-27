"""
Unit tests for the Ring corruption mechanic.
"""
import pytest
from engine.ring import Ring


class TestCorruptionTrack:
    """Corruption accumulation and loss threshold."""

    def test_starts_at_zero(self):
        ring = Ring()
        assert ring.corruption == 0

    def test_add_corruption_increments(self):
        ring = Ring()
        ring.add_corruption(5)
        assert ring.corruption == 5

    def test_add_corruption_capped_at_30(self):
        ring = Ring()
        ring.add_corruption(35)
        assert ring.corruption == 30

    def test_add_corruption_multiple_calls(self):
        ring = Ring()
        ring.add_corruption(10)
        ring.add_corruption(7)
        assert ring.corruption == 17

    def test_no_loss_below_30(self):
        ring = Ring()
        ring.add_corruption(29)
        assert ring.check_corruption_loss() is None

    def test_loss_at_30(self):
        ring = Ring()
        ring.add_corruption(30)
        assert ring.check_corruption_loss() == "fp"  # bearer defaults to fp

    def test_loss_at_30_for_shadow_bearer(self):
        ring = Ring()
        ring.bearer = "shadow"
        ring.add_corruption(30)
        assert ring.check_corruption_loss() == "shadow"


class TestCorruptionStatus:
    """get_corruption_status text output."""

    def test_low_corruption(self):
        ring = Ring()
        ring.add_corruption(5)
        status = ring.get_corruption_status()
        assert "5/30" in status
        assert "WARNING" not in status
        assert "DANGER" not in status
        assert "GAME OVER" not in status

    def test_warning_at_15(self):
        ring = Ring()
        ring.add_corruption(15)
        status = ring.get_corruption_status()
        assert "WARNING" in status

    def test_danger_at_20(self):
        ring = Ring()
        ring.add_corruption(20)
        status = ring.get_corruption_status()
        assert "DANGER" in status

    def test_game_over_at_30(self):
        ring = Ring()
        ring.add_corruption(30)
        status = ring.get_corruption_status()
        assert "GAME OVER" in status


class TestActivationFlags:
    """Per-turn activation gating."""

    def test_fp_can_activate_initially(self):
        ring = Ring()
        assert ring.can_activate_fp()

    def test_fp_cannot_activate_after_use(self):
        ring = Ring()
        ring.activate_fp("draw")
        assert not ring.can_activate_fp()

    def test_fp_cannot_activate_when_shadow_bears(self):
        ring = Ring()
        ring.bearer = "shadow"
        assert not ring.can_activate_fp()

    def test_shadow_cannot_activate_initially(self):
        ring = Ring()  # bearer defaults to fp
        assert not ring.can_activate_shadow()

    def test_shadow_can_activate_after_steal(self):
        ring = Ring()
        ring.steal_by_shadow()
        assert ring.can_activate_shadow()

    def test_start_turn_resets_flags(self):
        ring = Ring()
        ring.activate_fp("draw")
        assert not ring.can_activate_fp()
        ring.start_turn()
        assert ring.can_activate_fp()

    def test_shadow_activation_resets_on_start_turn(self):
        ring = Ring()
        ring.steal_by_shadow()
        ring.activate_shadow("drain")
        assert not ring.can_activate_shadow()
        ring.start_turn()
        assert ring.can_activate_shadow()


class TestActivationEffects:
    """Activation adds corruption."""

    def test_fp_activation_adds_2_corruption(self):
        ring = Ring()
        ring.activate_fp("draw")
        assert ring.corruption == 2

    def test_shadow_activation_adds_1_corruption(self):
        ring = Ring()
        ring.steal_by_shadow()
        ring.activate_shadow("drain")
        assert ring.corruption == 1  # Shadow only pays 1

    def test_fp_activation_cannot_exceed_turn_limit(self):
        ring = Ring()
        ring.activate_fp("draw")
        ring.activate_fp("willpower")  # Should be a no-op (already activated)
        assert ring.corruption == 2  # Not 4


class TestBearerMechanics:
    """Ring stealing and recovery."""

    def test_initial_bearer_is_fp(self):
        ring = Ring()
        assert ring.bearer == "fp"

    def test_shadow_steals_ring(self):
        ring = Ring()
        ring.steal_by_shadow()
        assert ring.bearer == "shadow"
        assert ring.shadow_bearer_turns == 0

    def test_fp_recovers_ring(self):
        ring = Ring()
        ring.steal_by_shadow()
        ring.recover_by_fp()
        assert ring.bearer == "fp"

    def test_steal_resets_activation_flags(self):
        ring = Ring()
        ring.activate_fp("draw")
        ring.steal_by_shadow()
        assert ring.can_activate_shadow()
        assert not ring.can_activate_fp()


class TestEndTurnPassiveCorruption:
    """Shadow bearing passive corruption every 2 turns."""

    def test_no_passive_corruption_first_shadow_turn(self):
        ring = Ring()
        ring.steal_by_shadow()
        ring.end_turn("shadow")
        assert ring.corruption == 0  # First turn, no corruption
        assert ring.shadow_bearer_turns == 1

    def test_passive_corruption_every_2_turns(self):
        ring = Ring()
        ring.steal_by_shadow()
        # Turn 1
        ring.end_turn("shadow")
        assert ring.corruption == 0
        # Turn 2
        ring.end_turn("shadow")
        assert ring.corruption == 1  # +1 every 2 turns

    def test_no_passive_corruption_when_fp_bears(self):
        ring = Ring()
        ring.end_turn("fp")
        assert ring.corruption == 0


class TestCorruptionTrackVisual:
    """corruption_track_str output."""

    def test_empty_track(self):
        ring = Ring()
        track = ring.corruption_track_str
        assert "0/30" in track

    def test_partial_track(self):
        ring = Ring()
        ring.add_corruption(12)
        track = ring.corruption_track_str
        assert "12/30" in track
