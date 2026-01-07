# Font1

What changed
- Added a font helper with fallback to pygame.freetype or blank surfaces.
- Updated UI screens and HUD to use the helper instead of pygame.font directly.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Verify the UI renders text (or at least no font-related crash).

Known issues
- If neither pygame.font nor pygame.freetype is available, text may be blank.
