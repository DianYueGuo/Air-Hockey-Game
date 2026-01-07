"""Window options and webcam view modes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WebcamViewMode(str, Enum):
    HIDDEN = "hidden"
    OVERLAY = "overlay"
    WINDOW = "window"


class ScoreboardMode(str, Enum):
    HUD = "hud"
    WINDOW = "window"


@dataclass
class WindowOptions:
    webcam_view_mode: WebcamViewMode = WebcamViewMode.HIDDEN
    scoreboard_mode: ScoreboardMode = ScoreboardMode.HUD
    fullscreen: bool = False
    display_index: int = 0
