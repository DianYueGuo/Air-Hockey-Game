# Air Hockey — Pygame + Webcam Ball Tracking

This repository builds a two-player air hockey game controlled by colored balls tracked via webcam.

## Quick Start

```bash
python -m air_hockey.main
```

## Controls
- **Menu:** click buttons
- **Play:** WASD (left mallet), Arrow keys (right mallet)
- **Pause:** ESC
- **Calibration:** Enter/Space to capture a step

## Settings
Settings are stored per user and apply when entering Play.

Available toggles:
- Webcam view (hidden/overlay/window)
- Scoreboard mode (HUD/window)
- Theme (default/retro)
- Sound pack (default/retro)
- Fullscreen + display index (restart app to apply)
- Vision tuning (smoothing)
- Physics tuning (puck restitution/damping, max speed, mallet speed)

## Docs
- Calibration flow: `docs/calibration.md`
- Build and packaging: `docs/build.md`
- Troubleshooting: `docs/troubleshooting.md`
