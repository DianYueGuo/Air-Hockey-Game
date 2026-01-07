# Live1

What changed
- Added live settings refresh when resuming Play from Pause.
- Applied updated physics, vision, theme, and audio settings without recreating the app.

Manual test steps
- Run `python -m air_hockey.main`.
- Start Play, open Pause -> Settings, change theme/sound/physics, then Continue.
- Verify changes apply immediately after resuming.

Known issues
- Fullscreen/display changes still require restart.
