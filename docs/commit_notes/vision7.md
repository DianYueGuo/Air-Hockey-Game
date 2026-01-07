# Vision7

What changed
- Replaced color-based tracking with MediaPipe hand detection.
- Simplified Vision Tuning to smoothing, detection scale, and max-jump filtering.
- Updated documentation for the new tracking pipeline.

Manual test steps
- Run `python3 -m air_hockey.main` (after installing mediapipe).
- Move hands in view; confirm mallets track palm centers.
- Adjust Vision Tuning values and observe tracking stability.

Known issues
- MediaPipe adds CPU cost; lower Detection Scale if needed.
