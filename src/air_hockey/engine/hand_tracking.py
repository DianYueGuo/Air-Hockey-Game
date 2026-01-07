"""Hand tracking using MediaPipe."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import cv2
try:
    import mediapipe as mp
except Exception as exc:  # pragma: no cover - runtime dependency check
    mp = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


@dataclass
class HandPositions:
    left: Optional[tuple[int, int]]
    right: Optional[tuple[int, int]]


class HandTracker:
    def __init__(self, process_every: int = 1) -> None:
        if mp is None:
            raise RuntimeError(
                "mediapipe is not available. Install mediapipe for Python 3.11/3.12 "
                "and ensure no local module named 'mediapipe' shadows it."
            ) from _IMPORT_ERROR
        if not hasattr(mp, "solutions"):
            raise RuntimeError(
                "mediapipe import succeeded but 'solutions' is missing. "
                "This usually means an incompatible version or a naming conflict."
            )
        self.process_every = max(1, process_every)
        self._frame_index = 0
        self._last_positions = HandPositions(left=None, right=None)
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, frame_bgr: cv2.Mat, scale: float = 1.0) -> HandPositions:
        self._frame_index += 1
        if self._frame_index % self.process_every != 0:
            return self._last_positions
        frame = frame_bgr
        if scale < 1.0:
            new_w = max(1, int(frame_bgr.shape[1] * scale))
            new_h = max(1, int(frame_bgr.shape[0] * scale))
            frame = cv2.resize(frame_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._hands.process(rgb)

        left_pos = None
        right_pos = None
        if results.multi_hand_landmarks and results.multi_handedness:
            for landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                label = handedness.classification[0].label.lower()
                cx, cy = self._palm_center(landmarks, frame.shape[1], frame.shape[0])
                if scale < 1.0:
                    cx = int(cx / scale)
                    cy = int(cy / scale)
                if label == "left" and left_pos is None:
                    left_pos = (cx, cy)
                elif label == "right" and right_pos is None:
                    right_pos = (cx, cy)
        self._last_positions = HandPositions(left=left_pos, right=right_pos)
        return self._last_positions

    @staticmethod
    def _palm_center(landmarks, width: int, height: int) -> tuple[int, int]:
        indices = [0, 5, 9, 13, 17]
        xs = [landmarks.landmark[i].x for i in indices]
        ys = [landmarks.landmark[i].y for i in indices]
        x = int(sum(xs) / len(xs) * width)
        y = int(sum(ys) / len(ys) * height)
        return (x, y)
