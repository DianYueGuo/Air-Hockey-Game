# Score1

What changed
- Scoreboard window now gracefully falls back to HUD if SDL2 renderer lacks texture support.

Manual test steps
- Run `python3 -m air_hockey.main` with scoreboard mode set to WINDOW.
- Verify no crash; HUD should appear if SDL2 texture support is unavailable.

Known issues
- Some pygame builds may not support a separate scoreboard window.
