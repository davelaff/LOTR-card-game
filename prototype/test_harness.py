#!/usr/bin/env python3
"""
Alpha test harness for LOTR Card Battle Game.
Runs automated games between faction combos and collects metrics + issues.
Usage: python test_harness.py --games N --fp <faction> --sh <faction>
"""

import sys
import os
import random
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.game import GameState, GamePhase
from engine.card import CardType, Faction
from ai.simple_ai import SimpleAI


def run_game(fp_faction: Faction, shadow_faction: Faction, max_turns: int = 50) -> dict:
    """
    Run a full automated game between two factions.
    Both sides use simple AI (FP also auto-played for testing speed).
    Returns a results dict with metrics, events, and issues.
    """
    result = {
        "fp_faction": fp_faction.value,
        "sh_faction": shadow_faction.value,
        "winner": None,
        "loss_reason": None,
        "total_turns": 0,
        "fp_influence_remaining": 0,
        "sh_influence_remaining": 0,
        "corruption": 0,
        "fp_cards_played": 0,
        "sh_cards_played": 0,
        "fp_allies_killed": 0,
        "sh_allies_killed": 0,
        "fp_hero_died": False,
        "sh_hero_died": False,
        "ring_activated_fp": 0,
        "ring_activated_sh": 0,
        "locations_flipped": 0,
        "issues": [],
        "events": [],
        "crashed": False,
        "crash_trace": None,
    }
    
    try:
        game = GameState()
        game.setup(fp_faction=fp_faction, shadow_faction=shadow_faction)
        
        fp_ai = SimpleAI(game)
        sh_ai = SimpleAI(game)
        
        turn_count = 0
        
        while not game.game_over and turn_count < max_turns:
            turn_count += 1
            
            # FP turn
            game.start_turn()
            fp_wp_before = game.fp_player.willpower_pool
            fp_hand_before = len(game.fp_player.hand)
            
            # FP turn: play cards, move allies, attack, then end
            if game.active_player == "fp" and not game.game_over:
                # 1. Play up to 3 affordable cards (prefer allies, cheapest first)
                fp_played = 0
                for card in sorted(game.fp_player.hand, key=lambda c: (c.card_type != CardType.ALLY, c.cost)):
                    if fp_played >= 3:
                        break
                    if card.cost <= game.fp_player.willpower_pool:
                        msgs = game.play_card(card, "fp")
                        result["fp_cards_played"] += 1
                        result["events"].append(f"T{turn_count}: FP plays {card.name} ({card.cost}WP)")
                        fp_played += 1
                
                # 2. Move up to 2 allies from deployment to locations
                board = game.board
                moved = 0
                for ally in list(board.fp_deployment):
                    if ally.tapped or moved >= 2:
                        continue
                    for loc_idx in [1, 0, 2]:
                        loc = board.get_location(loc_idx)
                        if len(loc.fp_front) < 3:
                            game.move_ally(ally, "fp", loc_idx, "front")
                            moved += 1
                            break
                
                # 3. Attack with available allies (up to 5 attacks)
                attacks = 0
                for loc_idx, loc in enumerate(board.locations):
                    if attacks >= 5:
                        break
                    for ally in loc.get_allies("fp"):
                        if attacks >= 5:
                            break
                        if ally.can_attack(game.fp_player.turn_number):
                            targets = loc.valid_attack_targets(ally, "fp")
                            if targets:
                                # Prefer weakest enemy ally, then location
                                best = None
                                for t_type, target in targets:
                                    if t_type != "location":
                                        if best is None or target.current_toughness < best[1].current_toughness:
                                            best = (t_type, target)
                                if best is None:
                                    for t_type, target in targets:
                                        if t_type == "location":
                                            best = (t_type, target)
                                            break
                                if best:
                                    result["events"].append(f"T{turn_count}: FP {ally.card.name} attacks")
                                    game.combat.resolve_attack(ally, "fp", best[1], best[0])
                                    attacks += 1
                
                # 4. Activate Ring regularly (50% chance if available — corruption clock)
                if game.ring.can_activate_fp() and random.random() < 0.5:
                    game.ring.activate_fp("draw")
                    game.fp_player.draw_cards(2)
                    result["ring_activated_fp"] += 1
                    result["events"].append(f"T{turn_count}: FP activates Ring (corruption {game.ring.corruption})")
                
                game.end_turn()
            
            if game.game_over:
                break
            
            # SH turn (AI)
            game.start_turn()
            if game.active_player == "shadow" and not game.game_over:
                sh_hand_before = len(game.shadow_player.hand)
                sh_msgs = sh_ai.take_turn()
                # Count cards played by AI
                for msg in sh_msgs:
                    if "Played" in msg:
                        result["sh_cards_played"] += 1
                        result["events"].append(f"T{turn_count}: SH plays {msg.split('Played ')[-1].split(' for')[0]}")
                    if "Ring activated" in msg:
                        result["ring_activated_sh"] += 1
                    if "flipped" in msg.lower():
                        result["locations_flipped"] += 1
                    if "has fallen" in msg:
                        result["fp_hero_died"] = True
                    if "GAME OVER" in msg:
                        result["events"].append(f"T{turn_count}: {msg}")
            
            if game.game_over:
                break
            
            # Check for stalemate (no cards played in 10 turns)
            if turn_count > 10:
                recent = result["events"][-5:]
                if all("plays" not in e.lower() for e in recent):
                    result["issues"].append(f"Possible stalemate at turn {turn_count}")
        
        # Capture final state
        result["winner"] = game.winner
        result["loss_reason"] = game.loss_reason
        result["total_turns"] = turn_count
        result["fp_influence_remaining"] = game.fp_player.influence
        result["sh_influence_remaining"] = game.shadow_player.influence
        result["corruption"] = game.ring.corruption
        
        # Analyze results
        if turn_count >= max_turns:
            result["issues"].append(f"Hit max turns ({max_turns}) — possible infinite game")
        
        if game.winner is None and not game.game_over:
            result["issues"].append("Game ended with no winner")
        
        # Balance checks
        if game.winner == "fp" and game.fp_player.influence > 25:
            result["issues"].append(f"FP stomp — won with {game.fp_player.influence} Influence remaining")
        if game.winner == "shadow" and game.shadow_player.influence > 25:
            result["issues"].append(f"SH stomp — won with {game.shadow_player.influence} Influence remaining")
        
        if game.ring.corruption >= 28 and game.winner is None:
            result["issues"].append("Corruption near loss threshold without game ending")
        
        # First-turn kill check
        if result["total_turns"] <= 3 and game.winner:
            result["issues"].append(f"Very short game ({result['total_turns']} turns) — balance concern")
        
    except Exception as e:
        result["crashed"] = True
        result["crash_trace"] = traceback.format_exc()
        result["issues"].append(f"CRASH: {str(e)}")
    
    return result


def print_result(result: dict):
    """Pretty-print a game result."""
    print(f"\n{'='*60}")
    print(f"  {result['fp_faction']} vs {result['sh_faction']}")
    print(f"{'='*60}")
    print(f"  Winner: {result['winner'] or 'NONE'}")
    if result['loss_reason']:
        print(f"  Reason: {result['loss_reason']}")
    print(f"  Turns: {result['total_turns']}")
    print(f"  FP Influence: {result['fp_influence_remaining']}/30")
    print(f"  SH Influence: {result['sh_influence_remaining']}/30")
    print(f"  Corruption: {result['corruption']}/30")
    print(f"  FP cards played: {result['fp_cards_played']}")
    print(f"  SH cards played: {result['sh_cards_played']}")
    print(f"  Ring activations: FP={result['ring_activated_fp']} SH={result['ring_activated_sh']}")
    print(f"  Locations flipped: {result['locations_flipped']}")
    print(f"  FP hero died: {result['fp_hero_died']}")
    print(f"  SH hero died: {result['sh_hero_died']}")
    print(f"  Crashed: {result['crashed']}")
    
    if result['issues']:
        print(f"\n  ISSUES FOUND ({len(result['issues'])}):")
        for issue in result['issues']:
            print(f"    ⚠ {issue}")
    
    if result['events']:
        print(f"\n  Key events ({len(result['events'])}):")
        for event in result['events'][:10]:
            print(f"    • {event}")
        if len(result['events']) > 10:
            print(f"    ... and {len(result['events']) - 10} more")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LOTR Card Game Alpha Test Harness")
    parser.add_argument("--games", type=int, default=3, help="Number of games to run per combo")
    parser.add_argument("--fp", type=str, default=None, help="Free Peoples faction")
    parser.add_argument("--sh", type=str, default=None, help="Shadow faction")
    parser.add_argument("--all", action="store_true", help="Test all possible combos")
    args = parser.parse_args()
    
    fp_factions = [Faction.GONDOR, Faction.ELVEN, Faction.DWARVEN, Faction.ROHAN, Faction.HOBBIT]
    sh_factions = [Faction.MORDOR, Faction.ISENGARD, Faction.MORIA, Faction.HARAD, Faction.NAZGUL]
    
    if args.fp:
        fp_factions = [Faction[args.fp.upper()]]
    if args.sh:
        sh_factions = [Faction[args.sh.upper()]]
    
    all_results = []
    
    if args.all:
        combos = [(fp, sh) for fp in fp_factions for sh in sh_factions]
        print(f"Running {len(combos)} faction combos × {args.games} games each = {len(combos) * args.games} games total\n")
    else:
        combos = [(fp_factions[0], sh_factions[0])]
        print(f"Running default combo × {args.games} games\n")
    
    for fp, sh in combos:
        for i in range(args.games):
            print(f"\n--- Game {i+1}/{args.games}: {fp.value} vs {sh.value} ---")
            result = run_game(fp, sh)
            all_results.append(result)
            print_result(result)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"  ALPHA TEST SUMMARY")
    print(f"{'='*60}")
    print(f"  Total games: {len(all_results)}")
    crashes = [r for r in all_results if r["crashed"]]
    print(f"  Crashes: {len(crashes)}")
    fp_wins = [r for r in all_results if r["winner"] == "fp"]
    sh_wins = [r for r in all_results if r["winner"] == "shadow"]
    print(f"  FP wins: {len(fp_wins)}, SH wins: {len(sh_wins)}")
    
    all_issues = []
    for r in all_results:
        all_issues.extend(r["issues"])
    
    if all_issues:
        print(f"\n  ALL ISSUES ({len(all_issues)}):")
        for issue in sorted(set(all_issues)):
            count = all_issues.count(issue)
            print(f"    [{count}x] {issue}")
    
    avg_turns = sum(r["total_turns"] for r in all_results) / max(1, len(all_results))
    print(f"\n  Average game length: {avg_turns:.1f} turns")
