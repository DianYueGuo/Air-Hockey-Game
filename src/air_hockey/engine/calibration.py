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


@dataclass
class CalibrationData:
    left: PlayerCalibration
    right: PlayerCalibration
