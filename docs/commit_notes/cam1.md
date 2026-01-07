# Cam1

What changed
- Flipped webcam frames horizontally to remove mirrored view in Play and Calibration.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Open Play and verify the overlay preview matches real-world left/right.
- Open Calibration and confirm the preview is no longer mirrored.

Known issues
- None.
