"""Hand tracking using MediaPipe Pose (wrist control)."""

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
        self._pose = mp.solutions.pose.Pose(
            model_complexity=1,
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
        results = self._pose.process(rgb)

        left_pos = None
        right_pos = None
        if results.pose_landmarks:
            left_pos = self._wrist_position(
                results.pose_landmarks, frame.shape[1], frame.shape[0], left=False
            )
            right_pos = self._wrist_position(
                results.pose_landmarks, frame.shape[1], frame.shape[0], left=True
            )
            if scale < 1.0:
                if left_pos is not None:
                    left_pos = (int(left_pos[0] / scale), int(left_pos[1] / scale))
                if right_pos is not None:
                    right_pos = (int(right_pos[0] / scale), int(right_pos[1] / scale))
        self._last_positions = HandPositions(left=left_pos, right=right_pos)
        return self._last_positions

    @staticmethod
    def _wrist_position(landmarks, width: int, height: int, left: bool) -> Optional[tuple[int, int]]:
        idx = (
            mp.solutions.pose.PoseLandmark.LEFT_WRIST
            if left
            else mp.solutions.pose.PoseLandmark.RIGHT_WRIST
        )
        landmark = landmarks.landmark[idx]
        if landmark.visibility < 0.5:
            return None
        x = int(landmark.x * width)
        y = int(landmark.y * height)
        return (x, y)
