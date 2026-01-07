# Vision8

What changed
- Added a clear runtime error when mediapipe is unavailable or incompatible.

Manual test steps
- Run `python3 -m air_hockey.main` without mediapipe installed.
- Confirm the error message explains how to fix mediapipe installation.

Known issues
- mediapipe currently requires a supported Python version (3.11/3.12).
