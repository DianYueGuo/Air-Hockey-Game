# G3b

What changed
- Added a Vision Tuning panel for smoothing in Settings.
- Applied EMA smoothing to camera-driven mallet positions.

Manual test steps
- Run `python -m air_hockey.main`.
- Open Settings -> Vision Tuning and adjust smoothing.
- Re-enter Play and observe steadier mallet movement.

Known issues
- Smoothing applies on re-entering Play; live updates are not applied.
