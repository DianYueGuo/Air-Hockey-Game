# Vision2

What changed
- Added HSV saturation/value max controls in Vision Tuning.
- Updated settings documentation accordingly.

Manual test steps
- Run `python -m air_hockey.main`.
- Open Settings -> Vision Tuning and adjust sat/val max values.
- Re-enter Play and confirm detection updates.

Known issues
- Conflicting HSV ranges can still break detection; Reset HSV if needed.
