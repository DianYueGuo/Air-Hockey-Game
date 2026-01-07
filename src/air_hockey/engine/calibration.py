"""Calibration data structures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerCalibration:
    cam_x_min: float | None = None
    cam_x_max: float | None = None
    cam_y_min: float | None = None
    cam_y_max: float | None = None

    def set_min_x(self, value: float) -> None:
        self.cam_x_min = value

    def set_max_x(self, value: float) -> None:
        self.cam_x_max = value

    def set_min_y(self, value: float) -> None:
        self.cam_y_min = value

    def set_max_y(self, value: float) -> None:
        self.cam_y_max = value

    def to_dict(self) -> dict[str, float | None]:
        return {
            "cam_x_min": self.cam_x_min,
            "cam_x_max": self.cam_x_max,
            "cam_y_min": self.cam_y_min,
            "cam_y_max": self.cam_y_max,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float | None]) -> "PlayerCalibration":
        return cls(
            cam_x_min=data.get("cam_x_min"),
            cam_x_max=data.get("cam_x_max"),
            cam_y_min=data.get("cam_y_min"),
            cam_y_max=data.get("cam_y_max"),
        )


@dataclass
class CalibrationData:
    left: PlayerCalibration
    right: PlayerCalibration

    def to_dict(self) -> dict[str, dict[str, float | None]]:
        return {
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, dict[str, float | None]]) -> "CalibrationData":
        return cls(
            left=PlayerCalibration.from_dict(data.get("left", {})),
            right=PlayerCalibration.from_dict(data.get("right", {})),
        )
