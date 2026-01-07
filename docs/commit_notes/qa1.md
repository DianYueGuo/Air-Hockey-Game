# QA1

What changed
- Audio manager falls back to the default sound pack if the selected pack is missing.
- Display cycling now uses the actual detected display count.

Manual test steps
- Rename a sound pack folder and verify audio still loads from default.
- Open Settings and cycle display index; confirm it wraps at the correct count.

Known issues
- None.
