#!/usr/bin/env python3
"""
LOTR Card Battle Game — CLI Prototype
=====================================
A text-based digital prototype of the Lord of the Rings card battle game.
Choose your faction and face off against the Shadow (or another Free Peoples).

Usage: python main.py
"""

import sys
import os

# Ensure the prototype directory is in the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.game import GameState, GamePhase
from engine.card import CardType, Faction
from ui.renderer import render_game_state, render_action_menu, render_messages
from ui.input_handler import InputHandler
from ai.simple_ai import SimpleAI


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print the game banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     THE LORD OF THE RINGS — Digital Card Battle Game         ║
║                     CLI Prototype v1.1                        ║
║                                                              ║
║   Commands:                                                  ║
║   [P1-P9] Play a card     [M] Move an ally                   ║
║   [A]     Declare attack  [H] Use Hero ability               ║
║   [R]     Activate Ring   [E] End turn                       ║
║   [Q]     Quit game                                          ║
╚══════════════════════════════════════════════════════════════╝
""")


def choose_faction(is_free_peoples: bool) -> Faction:
    """Let the player choose a faction."""
    if is_free_peoples:
        factions = [
            (Faction.GONDOR, "Gondor — Fortification Control"),
            (Faction.ELVEN, "Elven — Foresight Tempo"),
            (Faction.DWARVEN, "Dwarven — Treasure Hoard"),
            (Faction.ROHAN, "Rohan — Cavalry Charge"),
            (Faction.HOBBIT, "Hobbit — Ring-bearer's Burden"),
        ]
    else:
        factions = [
            (Faction.MORDOR, "Mordor — Orc Swarm, Corruption Burn"),
            (Faction.ISENGARD, "Isengard — Uruk-hai Efficiency"),
            (Faction.MORIA, "Moria — Ambush Swarm, Deep Tunnels"),
            (Faction.HARAD, "Harad — Mumakil Stampede"),
            (Faction.NAZGUL, "Nazgul — Terror Control"),
        ]
    
    print()
    side = "Free Peoples" if is_free_peoples else "Shadow"
    print(f"  Choose your {side} faction:")
    for i, (f, desc) in enumerate(factions):
        print(f"    [{i+1}] {f.value} — {desc}")
    
    while True:
        try:
            choice = input("  Choice [1-5] > ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(factions):
                return factions[idx][0]
        except (ValueError, EOFError):
            pass
        print("  Invalid choice. Enter 1-5.")


def choose_opponent(fp_faction: Faction) -> Faction:
    """Let the player choose which Shadow faction to face, or let the AI choose."""
    shadow_factions = [
        (Faction.MORDOR, "Mordor — Orc Swarm, Corruption Burn"),
        (Faction.ISENGARD, "Isengard — Uruk-hai Efficiency"),
        (Faction.MORIA, "Moria — Ambush Swarm, Deep Tunnels"),
        (Faction.HARAD, "Harad — Mumakil Stampede"),
        (Faction.NAZGUL, "Nazgul — Terror Control"),
    ]
    
    print()
    print("  Choose your Shadow opponent:")
    for i, (f, desc) in enumerate(shadow_factions):
        print(f"    [{i+1}] {f.value} — {desc}")
    print("    [R] Random")
    
    while True:
        try:
            choice = input("  Choice [1-5 or R] > ").strip().upper()
            if choice == "R":
                import random
                return random.choice(shadow_factions)[0]
            idx = int(choice) - 1
            if 0 <= idx < len(shadow_factions):
                return shadow_factions[idx][0]
        except (ValueError, EOFError):
            pass
        print("  Invalid choice. Enter 1-5 or R.")


def main():
    """Main game loop."""
    clear_screen()
    print_banner()
    
    # Faction selection
    fp_faction = choose_faction(is_free_peoples=True)
    shadow_faction = choose_opponent(fp_faction)
    
    clear_screen()
    print_banner()
    print(f"\n  Free Peoples: {fp_faction.value}  vs  Shadow: {shadow_faction.value}")
    print("  Setting up game...")
    
    # Initialize game
    game = GameState()
    game.setup(fp_faction=fp_faction, shadow_faction=shadow_faction)
    
    input_handler = InputHandler(game)
    ai = SimpleAI(game)
    
    # Start first turn (Free Peoples)
    game.start_turn()
    
    running = True
    while running and not game.game_over:
        player_state = game.get_player_state(game.active_player)
        
        if game.active_player == "shadow":
            # AI turn
            clear_screen()
            print(render_game_state(game))
            print(f"\n  --- Shadow ({shadow_faction.value}) AI is taking its turn ---\n")
            
            ai_msgs = ai.take_turn()
            for msg in ai_msgs:
                print(f"  > {msg}")
            
            # Check game over
            if game.game_over:
                break
            
            # Show post-AI board state so player can see what happened
            print(f"\n  --- AI turn complete. Current board: ---")
            print(render_game_state(game))
            input("\n  Press Enter to begin your turn...")
            
            # Start FP turn
            game.start_turn()
            continue
        
        # Player (Free Peoples) turn
        clear_screen()
        print(render_game_state(game))
        
        # Display status messages
        if game.phase_messages:
            print(render_messages(game.phase_messages))
            game.phase_messages = []
        
        print(render_action_menu(player_state, game))
        
        # Get input
        try:
            cmd = input("  Command > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Quitting...")
            break
        
        if not cmd:
            continue
        
        if cmd.upper() in ("Q", "QUIT"):
            print("  Thanks for playing!")
            break
        
        if cmd.upper() in ("E", "END"):
            game.end_turn()
            if game.game_over:
                break
            # Start shadow turn
            game.start_turn()
            continue
        
        # Process command
        msgs = input_handler.process_command(cmd)
        for msg in msgs:
            print(f"  > {msg}")
        
        if game.game_over:
            break
        
        # Small pause
        input("\n  Press Enter to continue...")
    
    # Game over screen
    clear_screen()
    print_banner()
    print(render_game_state(game))
    print()
    print("=" * 80)
    if game.winner == "fp":
        print("  🏆 FREE PEOPLES VICTORY! 🏆")
        print(f"  {game.loss_reason}")
    elif game.winner == "shadow":
        print("  💀 SHADOW VICTORY! 💀")
        print(f"  {game.loss_reason}")
    else:
        print("  Game ended.")
    print("=" * 80)
    print()
    print(f"  Final Ring Corruption: {game.ring.corruption}/30")
    print(f"  Free Peoples Influence: {game.fp_player.influence}")
    print(f"  Shadow Influence: {game.shadow_player.influence}")
    print()


if __name__ == "__main__":
    main()
