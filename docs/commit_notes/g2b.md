# G2b

What changed
- Added Settings toggles for fullscreen, display index, and swapping player color presets.

Manual test steps
- Run `python -m air_hockey.main`.
- Open Settings and toggle fullscreen/display, then exit.
- Restart the app to verify window changes.
- Swap player colors and verify ball colors map to opposite mallets.

Known issues
- Display index cycling assumes up to 3 displays; adjust if needed.
