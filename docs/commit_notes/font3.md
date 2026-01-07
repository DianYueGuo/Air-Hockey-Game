# Font3

What changed
- Added a bitmap font fallback so text remains visible without pygame.font or pygame.freetype.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Verify menu and UI text is visible even if pygame font modules are unavailable.

Known issues
- Bitmap font is uppercase and limited to basic characters.
