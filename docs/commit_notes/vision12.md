# Vision12

What changed
- Fixed right-hand mapping by treating detected hand positions as full-frame coordinates.
- Updated overlay markers to use full-frame normalization.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Move the right hand and confirm the marker aligns with the actual position.

Known issues
- If calibration data was captured with old mapping, recalibrate for best accuracy.
