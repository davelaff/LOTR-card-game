# Handoff — LOTR Card Battle Game

**Session:** Thursday, June 26, 2026  
**Repo:** https://github.com/davelaff/LOTR-card-game  
**Branch:** `main` (pushed and synced)

## What we built this session

1. **Git init** — repo created, 17 commits pushed to GitHub
2. **136 unit tests** across 6 test files covering all engine modules (BoardAlly, Ring, PlayerState, Board, CombatResolver, GameState)
3. **4 bugs fixed:**
   - Fear keyword didn't check temp keywords (combat.py — now uses `has_keyword()`)
   - Ring double-activation had no internal guard (ring.py — now returns None if already activated)
   - Renderer hardcoded "Gondor"/"Mordor" strings (now reads from `faction.value`)
   - Mordor deck size mismatch (31 cards, not 30 — test assertion fixed)
4. **Event system refactored** — 420-line if/elif chain in game.py extracted to `engine/events.py` with 29 per-card handler functions + `EVENT_HANDLERS` dispatch dict. game.py: 965 → 428 lines.
5. **5 "Simplified" event effects fleshed out** — The Last Debate, To Me! O My Kinsfolk!, The Last Alliance, The Straight Road, The Chasm Opens now do what their card text says instead of "Simplified: draw 1"
6. **Browser renderer built** — `ui/renderer_template.html` with Hearthstone-inspired dark LOTR theme, stone tabletop, 3-lane board, hero portrait panels, crystal willpower gems, corruption bar with red menace glow
7. **State exporter** — `engine/state_exporter.py` serializes full GameState to JSON for the browser
8. **Live browser integration** — `main.py` auto-opens browser on game start and refreshes after every action. `ui/browser_renderer.py` writes `game_view.html` with embedded game state.
9. **Hero art pipeline** — Aragorn (gondor.png) and Gothmog (mordor.png) generated and wired. Remaining 8 hero prompts written in `HERO_PROMPTS.md`.

## Current state

- **Engine:** Fully functional. All 10 factions playable. Turn flow, combat, ring mechanics, events all work.
- **Tests:** 136/136 pass. `pytest tests/` from project root.
- **UI:** ASCII CLI still works. Browser view auto-opens. Both views update in sync.
- **Art:** 2 of 10 hero cards generated (Gondor, Mordor). Pipeline proven — drop PNG into `prototype/ui/assets/heroes/[faction].png` and it appears on board.

## Where to pick up

### If Dave wants to generate more hero art
- `HERO_PROMPTS.md` at project root has exact prompts for all 8 remaining heroes
- Generate each, save to `prototype/ui/assets/heroes/[faction].png`
- Filenames: `elven.png`, `dwarven.png`, `rohan.png`, `hobbit.png`, `isengard.png`, `moria.png`, `harad.png`, `nazgul.png`
- No code changes needed — the pipeline picks them up automatically

### If Dave wants features
Priority order we discussed:
1. **PvP (human vs human)** — engine supports it, just needs UI for player 2 faction select + hand-hiding between turns. ~1 hour.
2. **Save/load game state** — serialize to JSON, resume games. Unlocks longer sessions. ~2 hours.
3. **Deck builder** — let players construct 30-card decks instead of fixed pre-cons. Major UX work.
4. **More card art** — unit cards (allies), location art, faction emblems, corner set pieces

### If Dave wants to just play
Run from prototype directory:
```
cd prototype
python main.py
```
Choose faction, browser opens automatically, play via terminal commands.

## Key files

| File | Purpose |
|---|---|
| `prototype/engine/game.py` | Game loop, turn flow, card play (428 lines) |
| `prototype/engine/events.py` | Event card handlers + dispatch dict (736 lines) |
| `prototype/engine/state_exporter.py` | GameState → JSON for browser |
| `prototype/engine/combat.py` | Attack resolution, keywords |
| `prototype/engine/board.py` | 3-lane board, rows, deployment |
| `prototype/engine/ring.py` | Corruption track, bearer mechanics |
| `prototype/engine/card.py` | Card dataclass, BoardAlly, keywords |
| `prototype/engine/player.py` | PlayerState, willpower, fatigue |
| `prototype/ui/renderer_template.html` | Browser board template (CSS/JS) |
| `prototype/ui/browser_renderer.py` | Embeds state into HTML template |
| `prototype/main.py` | CLI entry point + browser integration |
| `prototype/test_harness.py` | Automated AI-vs-AI testing |
| `tests/` | 136 unit tests across 6 files |
| `spikes/001-browser-renderer/` | Throwaway spike (reference only) |
| `HERO_PROMPTS.md` | 8 hero card image generation prompts |

## Running tests

```
cd C:/Users/dlafferty.MCNA/AppData/Local/hermes/projects/lotr-card-game
python -m pytest tests/ -q
```

```
cd prototype
python test_harness.py --games 3 --fp GONDOR --sh MORDOR
```

## Notes for the next agent

- The browser renderer is zero-dependency — pure HTML/CSS/JS, no server, no npm
- The template uses `// __GAME_STATE_PLACEHOLDER__` for state injection
- Hero images are referenced by convention: `ui/assets/heroes/{faction.value.lower()}.png`
- Game assets are committed to git (including hero PNGs) — they're part of the repo
- The event system uses a flat dict keyed by card name. Add new event cards by: (1) writing a handler function in events.py, (2) adding it to EVENT_HANDLERS dict
- Dave prefers direct communication, no sycophantic openers, no filler. Push back when wrong.
- Dave runs DeepSeek V4 Pro Max for deep reasoning, V4 Flash for general work.

## Dave's voice and preferences (from memory)

- Direct, no throat-clearing, no "would you like me to" closers
- Pushback is engagement — "I don't think that holds up" is respect
- Competence-based rapport, not performative enthusiasm
- Surgical edits — change only what's asked for, mention other issues don't auto-fix
- Prefers the agent to self-interrogate before committing to plans
- Tool output trumps agent reasoning — verify, don't assert
- Em dashes sparingly, no "not just X, but Y" constructions
