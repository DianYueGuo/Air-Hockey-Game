# UI1

What changed
- Added a pause overlay that dims the current game frame.

Manual test steps
- Run `python -m air_hockey.main`.
- Click Play and press Escape to pause.
- Verify the paused screen shows a dimmed snapshot behind the menu.

Known issues
- Snapshot captures the last rendered frame only.
