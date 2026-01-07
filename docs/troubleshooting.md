# Troubleshooting

## Settings and calibration not applying
- Settings and calibration load at screen start. If you change settings while in Play, return to the menu and re-enter Play.
- Ensure the user data directory is writable.

## Webcam issues
- Confirm the webcam is not in use by another app.
- If the overlay is black, try switching to WINDOW mode in Settings to see the raw feed.
- If detection feels noisy, recalibrate and ensure strong lighting.

## Audio issues
- If you hear no sound, check that your system audio output is not muted.
- Some systems block pygame.mixer initialization when no audio device is available.
