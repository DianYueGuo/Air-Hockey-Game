# Vision6

What changed
- Added downscaled detection for performance and stability.
- Enforced a minimum contour area to ignore tiny blobs.
- Added a max-jump filter to prevent impossible tracking jumps.
- Applied the same pipeline in Calibration.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Enable camera tracking and verify the point is steadier with fewer jumps.
- Toggle Motion Mask off to compare performance.

Known issues
- Advanced detection settings are stored in settings but not exposed in the UI.
