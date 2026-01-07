# Vision3

What changed
- Added background subtraction (MOG2) motion masking to reduce static background detections.
- Added a Motion Mask toggle in Settings and wired it to Play.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Open Settings and toggle Motion Mask to MOG2.
- Re-enter Play (or resume) and verify background noise is reduced.

Known issues
- MOG2 needs a brief warm-up; hold still for a second when starting Play.
