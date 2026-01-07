"""Camera capture in a background thread."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional

import cv2


@dataclass
class CameraFrame:
    frame: object
    timestamp: float


class CameraCapture:
    def __init__(self, device_index: int = 0) -> None:
        self.device_index = device_index
        self._capture: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._latest: Optional[CameraFrame] = None

    def start(self) -> bool:
        if self._running:
            return True
        self._capture = cv2.VideoCapture(self.device_index)
        if not self._capture.isOpened():
            self._capture.release()
            self._capture = None
            return False
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return True

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        self._thread = None
        if self._capture:
            self._capture.release()
        self._capture = None

    def get_latest(self) -> Optional[CameraFrame]:
        with self._lock:
            return self._latest

    def _run(self) -> None:
        while self._running and self._capture is not None:
            ok, frame = self._capture.read()
            if ok:
                with self._lock:
                    self._latest = CameraFrame(frame=frame, timestamp=time.time())
            else:
                time.sleep(0.01)
