"""Settings data structures."""

from __future__ import annotations

from dataclasses import dataclass

from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode


@dataclass
class Settings:
    theme: str = "default"
    webcam_view_mode: WebcamViewMode = WebcamViewMode.OVERLAY
    scoreboard_mode: ScoreboardMode = ScoreboardMode.HUD
    fullscreen: bool = False
    display_index: int = 0
    hsv_left: str = "orange"
    hsv_right: str = "tennis"
    smoothing: float = 0.2
    puck_restitution: float = 0.9
    puck_damping: float = 0.4
    max_puck_speed: float = 3.0
    mallet_speed_limit: float = 1.2

    def to_dict(self) -> dict[str, object]:
        return {
            "theme": self.theme,
            "webcam_view_mode": self.webcam_view_mode.value,
            "scoreboard_mode": self.scoreboard_mode.value,
            "fullscreen": self.fullscreen,
            "display_index": self.display_index,
            "hsv_left": self.hsv_left,
            "hsv_right": self.hsv_right,
            "smoothing": self.smoothing,
            "puck_restitution": self.puck_restitution,
            "puck_damping": self.puck_damping,
            "max_puck_speed": self.max_puck_speed,
            "mallet_speed_limit": self.mallet_speed_limit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Settings":
        return cls(
            theme=str(data.get("theme", "default")),
            webcam_view_mode=WebcamViewMode(str(data.get("webcam_view_mode", "overlay"))),
            scoreboard_mode=ScoreboardMode(str(data.get("scoreboard_mode", "hud"))),
            fullscreen=bool(data.get("fullscreen", False)),
            display_index=int(data.get("display_index", 0)),
            hsv_left=str(data.get("hsv_left", "orange")),
            hsv_right=str(data.get("hsv_right", "tennis")),
            smoothing=float(data.get("smoothing", 0.2)),
            puck_restitution=float(data.get("puck_restitution", 0.9)),
            puck_damping=float(data.get("puck_damping", 0.4)),
            max_puck_speed=float(data.get("max_puck_speed", 3.0)),
            mallet_speed_limit=float(data.get("mallet_speed_limit", 1.2)),
        )
