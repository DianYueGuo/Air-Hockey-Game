"""Theme loading and accessors."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
THEMES_DIR = PROJECT_ROOT / "assets" / "themes"


@dataclass(frozen=True)
class Theme:
    name: str
    table_background: tuple[int, int, int]
    table_border: tuple[int, int, int]
    table_center_line: tuple[int, int, int]
    puck: tuple[int, int, int]
    mallet_left: tuple[int, int, int]
    mallet_right: tuple[int, int, int]
    trail: tuple[int, int, int]
    hud_score: tuple[int, int, int]


class ThemeManager:
    def __init__(self, theme_name: str = "default") -> None:
        self.theme_name = theme_name
        self.theme = self._load_theme(theme_name)

    def _load_theme(self, theme_name: str) -> Theme:
        path = THEMES_DIR / f"{theme_name}.json"
        if not path.exists():
            path = THEMES_DIR / "default.json"
        data = json.loads(path.read_text())
        return Theme(
            name=data.get("name", "Default"),
            table_background=tuple(data["table"]["background"]),
            table_border=tuple(data["table"]["border"]),
            table_center_line=tuple(data["table"]["center_line"]),
            puck=tuple(data["entities"]["puck"]),
            mallet_left=tuple(data["entities"]["mallet_left"]),
            mallet_right=tuple(data["entities"]["mallet_right"]),
            trail=tuple(data["entities"]["trail"]),
            hud_score=tuple(data["hud"]["score"]),
        )
