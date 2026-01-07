# Vision4

What changed
- Set the default HSV preset for both players to orange.
- Calibration now uses the same preset for left/right by default.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Start Play with two orange balls and confirm both sides track.

Known issues
- Existing settings may still have the right preset set to tennis; use Swap Colors or Vision Tuning if needed.
