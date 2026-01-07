# Audio3

What changed
- Audio manager now handles missing pygame.mixer gracefully and skips sound loading.

Manual test steps
- Run `python3 -m air_hockey.main` in an environment without mixer support.
- Verify the app runs without crashing (audio disabled).

Known issues
- Audio will remain disabled if mixer is unavailable.
