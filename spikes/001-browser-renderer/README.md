# 001: Browser-Based Card Renderer

## Question
Can we render the LOTR card game in a browser with HTML/CSS that looks significantly better than ASCII and costs zero in dependencies?

## What we're testing
- Card frames with faction coloring and readable stats
- Board layout with 3 location zones + deployment areas
- Dark LOTR fantasy theme
- All rendering from machine-readable JSON (engine-exportable)
- Zero external assets — pure CSS art

## Approach
Single self-contained HTML file. Faction colors via CSS classes. 
Card frames are CSS borders and gradients. Stats positioned in corners.
Board is CSS Grid. A small Python script will later export GameState → JSON
that this HTML consumes.

## Files
- `renderer.html` — the standalone browser view
- `state_sample.json` — sample game state for testing
- `README.md` — this file

## Verdict
TBD after viewing in browser
