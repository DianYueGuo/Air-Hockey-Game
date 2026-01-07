# Release Checklist

- Replace placeholder icons in `assets/icons/` with real `app.ico`, `app.icns`, `app.png`.
- Verify assets are bundled correctly under PyInstaller on each OS.
- Run a full game flow: Menu -> Play -> Pause -> Settings -> Calibration.
- Confirm audio triggers: puck-wall, puck-mallet, goal, movement.
- Verify calibration persists across restarts and mapping feels correct.
- Validate webcam view modes: hidden/overlay/window.
- Validate scoreboard modes: HUD and separate window (if supported).
- Check performance (target 60 FPS rendering).
- Build executables for macOS, Windows, Linux.
- Update `docs/troubleshooting.md` with any known issues.
