# Font2

What changed
- Prefer pygame.freetype for text rendering to avoid pygame.font initialization issues.

Manual test steps
- Run `python3 -m air_hockey.main`.
- Verify menu text renders without missing labels.

Known issues
- If neither pygame.freetype nor pygame.font is available, text will be blank.
