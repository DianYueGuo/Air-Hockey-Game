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


def detect_largest_ball(frame: np.ndarray, hsv_range: HsvRange) -> DetectionResult:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array(hsv_range.lower), np.array(hsv_range.upper))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return DetectionResult(center=None, contour_area=0.0)

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    if area <= 0:
        return DetectionResult(center=None, contour_area=area)

    moments = cv2.moments(largest)
    if moments["m00"] == 0:
        return DetectionResult(center=None, contour_area=area)

    center_x = int(moments["m10"] / moments["m00"])
    center_y = int(moments["m01"] / moments["m00"])
    return DetectionResult(center=(center_x, center_y), contour_area=area)
