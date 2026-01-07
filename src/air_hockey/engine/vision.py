"""Color-based ball detection utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np


@dataclass(frozen=True)
class HsvRange:
    lower: tuple[int, int, int]
    upper: tuple[int, int, int]


HSV_PRESETS: dict[str, HsvRange] = {
    "orange": HsvRange(lower=(5, 120, 120), upper=(20, 255, 255)),
    "tennis": HsvRange(lower=(25, 80, 80), upper=(45, 255, 255)),
}


@dataclass
class DetectionResult:
    center: Optional[tuple[int, int]]
    contour_area: float


def resolve_hsv_range(
    preset_name: str, custom_range: dict[str, list[int]] | None
) -> HsvRange:
    if custom_range and "lower" in custom_range and "upper" in custom_range:
        lower = tuple(int(x) for x in custom_range["lower"])
        upper = tuple(int(x) for x in custom_range["upper"])
        return HsvRange(lower=lower, upper=upper)
    return HSV_PRESETS.get(preset_name, HSV_PRESETS["orange"])


def detect_largest_ball(
    frame: np.ndarray, hsv_range: HsvRange, min_area: float = 0.0
) -> DetectionResult:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_range.lower), np.array(hsv_range.upper))
    return _detect_from_mask(mask, min_area=min_area)


def detect_largest_ball_masked(
    frame: np.ndarray,
    hsv_range: HsvRange,
    motion_mask: np.ndarray,
    min_area: float = 0.0,
) -> DetectionResult:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    color_mask = cv2.inRange(hsv, np.array(hsv_range.lower), np.array(hsv_range.upper))
    combined = cv2.bitwise_and(color_mask, motion_mask)
    return _detect_from_mask(combined, min_area=min_area)


def _detect_from_mask(mask: np.ndarray, min_area: float = 0.0) -> DetectionResult:
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return DetectionResult(center=None, contour_area=0.0)

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area <= min_area:
        return DetectionResult(center=None, contour_area=area)

    moments = cv2.moments(largest)
    if moments["m00"] == 0:
        return DetectionResult(center=None, contour_area=area)

    center_x = int(moments["m10"] / moments["m00"])
    center_y = int(moments["m01"] / moments["m00"])
    return DetectionResult(center=(center_x, center_y), contour_area=area)


class MotionMasker:
    def __init__(self) -> None:
        self.subtractor = cv2.createBackgroundSubtractorMOG2(
            history=200, varThreshold=16, detectShadows=False
        )

    def apply(self, frame: np.ndarray) -> np.ndarray:
        mask = self.subtractor.apply(frame)
        _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
        return mask
