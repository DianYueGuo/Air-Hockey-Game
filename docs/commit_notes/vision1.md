# Vision1

What changed
- Added HSV range editing controls in Vision Tuning.
- Stored custom HSV ranges in settings and used them for detection.

Manual test steps
- Run `python -m air_hockey.main`.
- Open Settings -> Vision Tuning and adjust hue/sat/val mins.
- Re-enter Play and verify detection responds to changes.

Known issues
- HSV min/max ranges can be set to conflicting values; use Reset HSV if tracking fails.
