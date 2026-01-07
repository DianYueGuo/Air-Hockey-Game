# Status Checklist

## Core Gameplay
- [x] Puck + mallets + walls physics (Box2D)
- [x] Keyboard control for mallets (temporary)
- [x] Goal detection + scoring + reset
- [x] HUD scoreboard

## Audio & Visuals
- [x] Collision + goal sounds
- [x] Puck movement sound scaled by speed
- [x] Basic trail effect

## Webcam Tracking
- [x] Camera thread + latest frame
- [x] HSV detection presets
- [x] Naive mapping to mallets
- [x] View modes (hidden/overlay/window)

## Calibration
- [x] Guided calibration flow
- [x] Persist calibration
- [x] Debug overlays

## Settings & Themes
- [x] Theme system (default/retro)
- [x] Settings persistence
- [x] Sound pack selection
- [x] Physics + vision tuning panels

## Windows & Menus
- [x] Menu screen
- [x] Pause screen
- [x] Scoreboard window (best-effort)
- [x] Fullscreen + display index (best-effort)

## Packaging & Docs
- [x] PyInstaller spec
- [x] Build docs
- [x] Calibration docs
- [x] Settings docs
- [x] Troubleshooting
- [x] Release checklist

## Tests
- [x] Config roundtrip
- [x] Vision normalization

## Remaining Gaps
- [ ] Replace placeholder icons and sounds with real assets
- [ ] Live apply settings without re-entering Play (optional)
- [ ] UI polish pass (fonts, spacing, background dim on pause)
