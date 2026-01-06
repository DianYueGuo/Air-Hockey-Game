# Air Hockey — Box2D + Pygame + Webcam Ball Tracking (Codex-Driven Build)

You are Codex. This repository is empty or incomplete. Your job is to build the complete game described below, end-to-end, by implementing code and assets structure. You must proceed incrementally, producing small, reviewable changes suitable for commit-by-commit development.

Do not ask the human to design the architecture. Design it yourself within the constraints and acceptance criteria here. If anything is ambiguous, make a reasonable default and document it in `docs/decisions.md`.

---

## 0) Primary Goal

Build a 2-player air hockey game in **Python** using:

- **Box2D** for physics
- **Pygame** for graphics and audio
- **OpenCV** for webcam tracking of **orange/tennis balls** held by players

Players control mallets by moving hands holding balls in the air. The game maps detected ball positions to mallet positions.

The finished game must support:
- Menu: **Play / Settings / Calibration / Quit**
- Pause menu (in-game): **Continue / Settings / Calibration / Restart / Quit**
- Multiple field **themes**
- Sound effects: collisions, goals, puck movement
- Optional webcam detection view:
  - hidden
  - small overlay bottom-center in game window
  - separate window (for laptop screen while game projects to TV)
- Scoreboard:
  - traditional in-game HUD
  - OR separate scoreboard window (laptop screen)
- Calibration flow to set left/right/top/bottom bounds for each player by posing at extremes
- Cross-platform standalone executables (macOS, Windows, Linux) with proper icon via PyInstaller

---

## 1) Hard Constraints

### 1.1 Incremental delivery (commit-by-commit)
Work in small steps. Each step must:
- compile/run
- include minimal necessary files
- include clear manual test instructions in commit message text (write them in `docs/commit_notes/<date>-<slug>.md` if needed)

### 1.2 Minimize churn
- Do not refactor unrelated code.
- Do not rename files unless necessary.
- Prefer adding code over rearranging existing working code.

### 1.3 Performance and stability
- Main loop must remain responsive (target 60 FPS rendering).
- Camera capture must never block the render loop (use a thread + latest-frame queue).
- Physics must use a **fixed timestep** (e.g., 1/120 sec) with accumulator.

---

## 2) Definition of Done (DoD)

The project is done when:
1. Two players can play a full match using tracked balls to control mallets.
2. Calibration reliably maps each player’s ball positions into the table coordinates.
3. Webcam view modes work (hidden / overlay / separate window).
4. Scoreboard works (HUD and separate window).
5. Settings persist across runs.
6. Themes are selectable and change visuals + at least one sound set.
7. Sound effects are present for:
   - puck-wall hit
   - puck-mallet hit
   - goal scored
   - subtle puck movement effect (volume scaled by speed)
8. Pause menu works and can reach settings/calibration without crashing.
9. PyInstaller builds produce standalone executables on each OS, with icons and bundled assets.

---

## 3) Repository Structure (You must create this)

Use this layout (create missing directories/files):

```
air-hockey/
├── README.md
├── LICENSE
├── pyproject.toml
├── assets/
│   ├── icons/
│   ├── sounds/
│   │   ├── default/
│   │   │   ├── puck_hit_wall.wav
│   │   │   ├── puck_hit_mallet.wav
│   │   │   ├── goal.wav
│   │   │   └── puck_move.wav
│   │   └── retro/
│   │       └── ...
│   ├── themes/
│   │   ├── default.json
│   │   └── retro.json
│   └── fonts/
├── docs/
│   ├── decisions.md
│   ├── build.md
│   ├── calibration.md
│   ├── troubleshooting.md
│   └── commit_notes/
├── src/
│   └── air_hockey/
│       ├── __init__.py
│       ├── main.py
│       ├── app.py
│       ├── config/
│       │   ├── defaults.json
│       │   └── io.py
│       ├── engine/
│       │   ├── clock.py
│       │   ├── audio.py
│       │   ├── windowing.py
│       │   ├── camera.py
│       │   ├── vision.py
│       │   ├── calibration.py
│       │   ├── physics.py
│       │   └── render.py
│       ├── game/
│       │   ├── entities.py
│       │   ├── field.py
│       │   ├── rules.py
│       │   └── themes.py
│       └── ui/
│           ├── widgets.py
│           └── screens/
│               ├── menu.py
│               ├── play.py
│               ├── settings.py
│               ├── calibration.py
│               ├── pause.py
│               └── hud.py
├── tools/
│   └── package/
│       └── pyinstaller.spec
└── tests/
    ├── test_config.py
    └── test_vision.py
```

Notes:
- Keep code in `src/air_hockey` with `pyproject.toml` configured for `src` layout.
- Store runtime user data (settings/calibration) in an OS-appropriate per-user directory:
  - macOS: `~/Library/Application Support/AirHockey/`
  - Windows: `%APPDATA%\AirHockey\`
  - Linux: `~/.local/share/airhockey/`
  Use a small helper in `config/io.py`.

---

## 4) Dependencies (pyproject.toml)

Use Python 3.11+.

Add dependencies:
- `pygame`
- `opencv-python`
- `box2d-py`
- `numpy`

Dev dependencies:
- `pyinstaller`
- `pytest`

Implement `python -m air_hockey.main` as the entry point for dev.

---

## 5) Core Design Requirements

### 5.1 Game world
- Table rectangle with walls; goals at left/right (or top/bottom) — choose one and document.
- Two mallets constrained to their half (player 1 left, player 2 right) OR (top/bottom) — choose one and document.
- Puck with max speed clamp, mild damping; mallets are kinematic or dynamic with strong control constraints (choose best-feeling).
- Scoring increments when puck crosses goal line; reset puck/mallets after goal.

### 5.2 Tracking and mapping
- Detect colored balls using HSV thresholding with adjustable ranges.
- Provide defaults for orange and tennis ball “yellow-green” and allow adjusting thresholds in Settings.
- For each player:
  - Track one ball (largest contour of correct color in player ROI or half-frame).
  - Smooth with EMA.
  - Convert camera coordinates to table coordinates via calibration bounds:
    - calibration records (cam_x_min, cam_x_max, cam_y_min, cam_y_max)
    - mapping: normalize to [0,1], then scale to mallet range in game coordinates
  - Clamp to table and to player half.

### 5.3 Windows and display modes
- Main game window (Pygame).
- Webcam detection view modes:
  - hidden
  - overlay bottom-center (small surface)
  - separate OpenCV window (or a second Pygame window if feasible; if not feasible, OpenCV window is acceptable).
- Scoreboard modes:
  - HUD in game window
  - separate window (prefer Pygame second window; if difficult cross-platform, use a simple separate Pygame display if supported; otherwise document fallback using a borderless always-on-top small window if possible).

Document OS limitations if multi-window support varies.

### 5.4 UI/menus
Implement screens:
- Menu: Play / Settings / Calibration / Quit
- Settings:
  - theme selection
  - physics params (at least: puck restitution, puck damping, max puck speed, mallet speed limit)
  - vision params (HSV preset selection, sensitivity/smoothing)
  - window options (fullscreen/windowed, display index if possible, webcam view mode, scoreboard mode)
- Calibration:
  - guided steps:
    - Leftmost, Rightmost, Topmost, Bottommost
  - show live tracking and current detected point
  - save per-player calibration
- Pause menu in-game with options listed above.

All UI must be navigable via keyboard/mouse; camera-only control is not required.

---

## 6) Assets

You must provide:
- at least 2 themes (e.g., `default`, `retro`) via `assets/themes/*.json`
- at least 1 complete sound pack (`assets/sounds/default`)
- placeholder assets are acceptable initially, but must be non-empty and functional.
- proper icons in `assets/icons`:
  - `app.ico` (Windows)
  - `app.icns` (macOS)
  - `app.png` (Linux)

If you cannot create binary icon formats programmatically, add clear instructions in `docs/build.md` and include placeholder files with the expected names.

---

## 7) Build & Distribution

### 7.1 Development run
Must work with:
```bash
python -m air_hockey.main
```

### 7.2 Packaging
Provide:

- `tools/package/pyinstaller.spec`

- `docs/build.md` with per-OS build commands

- ensure assets are bundled and load correctly under PyInstaller

- executable name: `AirHockey` (or `AirHockey.exe` on Windows)

---

## 8) Testing
Add minimal tests:

- config load/save roundtrip (`tests/test_config.py`)

- vision mapping normalization correctness (`tests/test_vision.py`) using synthetic values (no webcam needed)

---

## 9) Milestone Plan (Implement in this order)
You must follow this order. Each milestone should be deliverable and runnable.

### Milestone A — App Skeleton
A1. `pyproject.toml` + package layout + run entry

A2. Basic Pygame window, event loop, screen manager

A3. Menu screen with placeholder buttons

A4. Settings and Calibration screens as placeholders

A5. `docs/decisions.md` initial entries

### Milestone B — Physics Playable (No webcam yet)
B1. Box2D world with puck + 2 mallets + walls

B2. Keyboard/mouse control for mallets (temporary)

B3. Goal + score + reset

B4. HUD scoreboard

### Milestone C — Audio + Visual Effects (basic)
C1. Load sounds; play on collisions and goals

C2. Puck movement sound scaled by speed

C3. Basic trail or impact flash effect (optional but preferred)

### Milestone D — Webcam Tracking
D1. Camera thread + latest frame

D2. HSV detection for orange + tennis presets

D3. Map detection -> mallet control (still without calibration; naive mapping)

D4. Toggle webcam view mode (hidden/overlay/separate)

### Milestone E — Calibration
E1. Calibration flow capturing extremes for each player

E2. Persist calibration and use it for mapping

E3. Live preview and debugging overlays

### Milestone F — Window Options + Scoreboard Window
F1. Scoreboard mode: HUD vs separate window

F2. Fullscreen and display selection (best effort; document limitations)

### Milestone G — Themes + Persisted Settings
G1. Theme system loading from JSON

G2. Settings persistence

G3. Physics/vision/window settings apply live (or on restart; document)

### Milestone H — Packaging
H1. PyInstaller spec; assets bundling; icons

H2. Build docs + troubleshooting

H3. Release checklist

---

## 10) Operating Instructions for Codex (How to work)
For each milestone step:

1. Implement the smallest working slice.

2. Update or create any needed docs.

3. Ensure `python -m air_hockey.main` runs without errors.

4. Add a short section to `docs/commit_notes/<step>.md`:

    - What changed

    - Manual test steps

    - Known issues

5. Move to the next step.

If a step requires a choice (e.g., left/right goals vs top/bottom goals), choose one quickly and document in `docs/decisions.md`.

---

## 11) Acceptance: What the human will do
The human will:

- run the game frequently

- review diffs

- commit after each step

- use Codex to implement next steps using this README as the only specification

Therefore:

- keep changes small

- keep everything runnable

- keep docs updated

- avoid “big bang” commits

---

## 12) Start Here
Implement Milestone A1 now:

- Create `pyproject.toml` with dependencies

- Create `src/air_hockey/main.py` with a basic runnable window loop stub

- Confirm run command works

- Create `docs/decisions.md` with initial recorded decisions
