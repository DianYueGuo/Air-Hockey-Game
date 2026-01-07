# Vision11

What changed
- Assigned left/right hands by screen position instead of MediaPipe handedness to avoid flipped offsets.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Move each hand and confirm the left/right tracking points align correctly.

Known issues
- If both hands are on one side, assignment will still pick leftmost/rightmost positions.
