# Calibration Guide

## Overview
Calibration maps camera coordinates to table space. Each player captures their left/right/top/bottom extremes by holding the tracked ball at the edge of their movement range.

## Steps
1. Open Calibration from the main menu.
2. Follow the prompt at the top (Leftmost, Rightmost, Topmost, Bottommost).
3. Hold the ball steady at the requested extreme and press Capture (or Enter/Space).
4. Repeat for both players until the flow completes.

## Tips
- Use bright, even lighting.
- Keep the camera fixed and avoid moving it during calibration.
- If detection is unstable, reduce background clutter and recalibrate.

## Where data is stored
Calibration is saved per user:
- macOS: `~/Library/Application Support/AirHockey/calibration.json`
- Windows: `%APPDATA%\AirHockey\calibration.json`
- Linux: `~/.local/share/airhockey/calibration.json`
