# Build & Packaging

## Dependencies
- Python 3.11+
- Install dev dependencies:
  - `pip install -e .[dev]`

## MediaPipe note
- Hand tracking uses `mediapipe==0.10.14` and requires Python 3.11 or 3.12.
- If you use Python 3.13+, MediaPipe will be skipped by pip and hand tracking will fail.

## PyInstaller build
From the project root:

```bash
pyinstaller tools/package/pyinstaller.spec
```

Outputs:
- macOS/Linux: `dist/AirHockey`
- Windows: `dist/AirHockey.exe`

## Icons
Placeholder icons are in `assets/icons/`:
- `app.ico` for Windows
- `app.icns` for macOS
- `app.png` for Linux

Replace them with real icons before release. If you cannot generate `ico`/`icns` formats, use a GUI tool and keep the filenames.

## Notes
- The spec bundles the entire `assets/` directory.
- Multi-window scoreboard uses `pygame._sdl2` when available; otherwise HUD is used.
