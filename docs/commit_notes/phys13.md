# Phys13

What changed
- Disabled puck speed clamping when max speed is set to 0.
- Reset Physics now clears the speed clamp for maximum glide.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Open Settings -> Physics Tuning and click Reset Physics.
- Re-enter Play and confirm the puck retains velocity.

Known issues
- None.
