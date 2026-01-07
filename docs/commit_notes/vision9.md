# Vision9

What changed
- Added hand detection frame skipping to reduce CPU load.
- Lowered default detection scale for faster tracking.
- Exposed process-every-N-frames control in Vision Tuning.

Manual test steps
- Run `python3 -m air_hockey.main`.
- In Settings -> Vision Tuning, increase Process Every to 2–3.
- Verify CPU usage drops and tracking remains usable.

Known issues
- Higher values reduce responsiveness.
