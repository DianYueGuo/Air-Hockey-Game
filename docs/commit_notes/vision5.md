# Vision5

What changed
- Added a "Same Color" toggle to force both players to use the same HSV preset.
- Play now applies the same HSV range when the toggle is enabled.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Open Settings and ensure Same Color is ON.
- Re-enter Play and verify both players track the same ball color.

Known issues
- If you want different colors per player, turn Same Color OFF and tune each preset.
