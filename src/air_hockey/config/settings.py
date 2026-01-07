"""Settings data structures."""

from __future__ import annotations

from dataclasses import dataclass

from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode


@dataclass
class Settings:
    theme: str = "default"
    sound_pack: str = "default"
    webcam_view_mode: WebcamViewMode = WebcamViewMode.OVERLAY
    scoreboard_mode: ScoreboardMode = ScoreboardMode.HUD
    fullscreen: bool = False
    display_index: int = 0
    hsv_left: str = "orange"
    hsv_right: str = "orange"
    smoothing: float = 0.2
    puck_restitution: float = 0.6
    puck_damping: float = 0.6
    max_puck_speed: float = 1.0
    mallet_speed_limit: float = 2.0
    hsv_left_range: dict[str, list[int]] | None = None
    hsv_right_range: dict[str, list[int]] | None = None
    motion_mask_mode: str = "off"
    force_same_hsv: bool = True
    detection_scale: float = 0.35
    min_contour_area: float = 200.0
    max_jump_px: float = 80.0
    hand_process_every: int = 2

    def to_dict(self) -> dict[str, object]:
        return {
            "theme": self.theme,
            "sound_pack": self.sound_pack,
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
            "hsv_left_range": self.hsv_left_range,
            "hsv_right_range": self.hsv_right_range,
            "motion_mask_mode": self.motion_mask_mode,
            "force_same_hsv": self.force_same_hsv,
            "detection_scale": self.detection_scale,
            "min_contour_area": self.min_contour_area,
            "max_jump_px": self.max_jump_px,
            "hand_process_every": self.hand_process_every,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Settings":
        defaults = cls()
        return cls(
            theme=str(data.get("theme", defaults.theme)),
            sound_pack=str(data.get("sound_pack", defaults.sound_pack)),
            webcam_view_mode=WebcamViewMode(
                str(data.get("webcam_view_mode", defaults.webcam_view_mode.value))
            ),
            scoreboard_mode=ScoreboardMode(
                str(data.get("scoreboard_mode", defaults.scoreboard_mode.value))
            ),
            fullscreen=bool(data.get("fullscreen", defaults.fullscreen)),
            display_index=int(data.get("display_index", defaults.display_index)),
            hsv_left=str(data.get("hsv_left", defaults.hsv_left)),
            hsv_right=str(data.get("hsv_right", defaults.hsv_right)),
            smoothing=float(data.get("smoothing", defaults.smoothing)),
            puck_restitution=float(data.get("puck_restitution", defaults.puck_restitution)),
            puck_damping=float(data.get("puck_damping", defaults.puck_damping)),
            max_puck_speed=float(data.get("max_puck_speed", defaults.max_puck_speed)),
            mallet_speed_limit=float(data.get("mallet_speed_limit", defaults.mallet_speed_limit)),
            hsv_left_range=data.get("hsv_left_range", defaults.hsv_left_range),
            hsv_right_range=data.get("hsv_right_range", defaults.hsv_right_range),
            motion_mask_mode=str(data.get("motion_mask_mode", defaults.motion_mask_mode)),
            force_same_hsv=bool(data.get("force_same_hsv", defaults.force_same_hsv)),
            detection_scale=float(data.get("detection_scale", defaults.detection_scale)),
            min_contour_area=float(data.get("min_contour_area", defaults.min_contour_area)),
            max_jump_px=float(data.get("max_jump_px", defaults.max_jump_px)),
            hand_process_every=int(data.get("hand_process_every", defaults.hand_process_every)),
        )
