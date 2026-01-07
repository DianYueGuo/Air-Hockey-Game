"""Calibration screen with guided steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame

from air_hockey.config.io import save_calibration
from air_hockey.engine.calibration import CalibrationData, PlayerCalibration
from air_hockey.engine.camera import CameraCapture
from air_hockey.engine.vision import HSV_PRESETS, detect_largest_ball
from air_hockey.ui.widgets import Button


@dataclass(frozen=True)
class CalibrationStep:
    player: str
    label: str
    axis: str


class CalibrationScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.font = pygame.font.SysFont("arial", 26)
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.back_button = Button(
            rect=pygame.Rect(40, window_size[1] - 80, 140, 44),
            label="Back",
            on_click=self._exit,
            font=self.font,
        )
        self.capture_button = Button(
            rect=pygame.Rect(window_size[0] - 180, window_size[1] - 80, 140, 44),
            label="Capture",
            on_click=self._capture_step,
            font=self.font,
        )
        self.camera = CameraCapture()
        self.camera_active = self.camera.start()
        self.hsv_left = HSV_PRESETS["orange"]
        self.hsv_right = HSV_PRESETS["tennis"]
        self.last_detection_left: tuple[int, int] | None = None
        self.last_detection_right: tuple[int, int] | None = None
        self.steps = self._build_steps()
        self.step_index = 0
        self.calibration = CalibrationData(
            left=PlayerCalibration(),
            right=PlayerCalibration(),
        )
        self.status_message = ""

    def _build_steps(self) -> list[CalibrationStep]:
        return [
            CalibrationStep(player="left", label="Left Player: Leftmost", axis="min_x"),
            CalibrationStep(player="left", label="Left Player: Rightmost", axis="max_x"),
            CalibrationStep(player="left", label="Left Player: Topmost", axis="min_y"),
            CalibrationStep(player="left", label="Left Player: Bottommost", axis="max_y"),
            CalibrationStep(player="right", label="Right Player: Leftmost", axis="min_x"),
            CalibrationStep(player="right", label="Right Player: Rightmost", axis="max_x"),
            CalibrationStep(player="right", label="Right Player: Topmost", axis="min_y"),
            CalibrationStep(player="right", label="Right Player: Bottommost", axis="max_y"),
        ]

    def _exit(self) -> None:
        if self.camera_active:
            self.camera.stop()
        self.on_back()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._exit()
                return
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._capture_step()
                return
        self.back_button.handle_event(event)
        self.capture_button.handle_event(event)

    def update(self, dt: float) -> None:
        self._update_detection()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 24, 28))
        title_surf = self.title_font.render("Calibration", True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 90))
        surface.blit(title_surf, title_rect)

        step = self.steps[self.step_index] if self.step_index < len(self.steps) else None
        if step:
            step_surf = self.font.render(step.label, True, (200, 210, 220))
            step_rect = step_surf.get_rect(center=(self.window_size[0] // 2, 160))
            surface.blit(step_surf, step_rect)

        help_text = "Hold the ball at the extreme and press Capture"
        help_surf = self.small_font.render(help_text, True, (170, 180, 190))
        help_rect = help_surf.get_rect(center=(self.window_size[0] // 2, 200))
        surface.blit(help_surf, help_rect)

        if self.status_message:
            status_surf = self.small_font.render(self.status_message, True, (180, 190, 200))
            status_rect = status_surf.get_rect(center=(self.window_size[0] // 2, 240))
            surface.blit(status_surf, status_rect)

        self._draw_debug_values(surface)

        self._draw_preview(surface)
        self.back_button.draw(surface)
        self.capture_button.draw(surface)

    def _update_detection(self) -> None:
        if not self.camera_active:
            return
        frame = self.camera.get_latest()
        if frame is None:
            return
        frame_height, frame_width = frame.frame.shape[:2]
        mid_x = frame_width // 2

        left_frame = frame.frame[:, :mid_x]
        right_frame = frame.frame[:, mid_x:]

        left_result = detect_largest_ball(left_frame, self.hsv_left)
        right_result = detect_largest_ball(right_frame, self.hsv_right)

        self.last_detection_left = left_result.center
        self.last_detection_right = right_result.center

    def _capture_step(self) -> None:
        if self.step_index >= len(self.steps):
            self.status_message = "Calibration complete."
            return
        step = self.steps[self.step_index]
        detection = self._current_detection(step.player)
        if detection is None:
            self.status_message = "No ball detected. Try again."
            return
        if step.player == "left":
            target = self.calibration.left
        else:
            target = self.calibration.right

        value = detection[0] if "x" in step.axis else detection[1]
        if step.axis == "min_x":
            target.set_min_x(value)
        elif step.axis == "max_x":
            target.set_max_x(value)
        elif step.axis == "min_y":
            target.set_min_y(value)
        elif step.axis == "max_y":
            target.set_max_y(value)

        save_calibration(self.calibration)

        self.step_index += 1
        if self.step_index >= len(self.steps):
            self.status_message = "Calibration complete. Press Back."
        else:
            self.status_message = "Captured. Proceed to next step."

    def _current_detection(self, player: str) -> tuple[int, int] | None:
        if player == "left":
            return self.last_detection_left
        return self.last_detection_right

    def _draw_preview(self, surface: pygame.Surface) -> None:
        frame = self.camera.get_latest()
        if frame is None:
            return
        frame_bgr = frame.frame
        frame_rgb = frame_bgr[:, :, ::-1]
        preview_width = 320
        preview_height = int(preview_width * frame_rgb.shape[0] / frame_rgb.shape[1])
        preview = pygame.transform.smoothscale(
            pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1)),
            (preview_width, preview_height),
        )
        preview_rect = preview.get_rect()
        preview_rect.center = (self.window_size[0] // 2, self.window_size[1] // 2 + 60)
        surface.blit(preview, preview_rect)

        if self.last_detection_left:
            self._draw_detection_circle(surface, preview_rect, self.last_detection_left, left=True)
        if self.last_detection_right:
            self._draw_detection_circle(surface, preview_rect, self.last_detection_right, left=False)

    def _draw_debug_values(self, surface: pygame.Surface) -> None:
        left = self.calibration.left
        right = self.calibration.right
        lines = [
            f\"Left X: {left.cam_x_min} .. {left.cam_x_max}\",
            f\"Left Y: {left.cam_y_min} .. {left.cam_y_max}\",
            f\"Right X: {right.cam_x_min} .. {right.cam_x_max}\",
            f\"Right Y: {right.cam_y_min} .. {right.cam_y_max}\",
        ]
        start_y = 280
        for index, line in enumerate(lines):
            surf = self.small_font.render(line, True, (150, 165, 175))
            surface.blit(surf, (40, start_y + index * 22))

    def _draw_detection_circle(
        self,
        surface: pygame.Surface,
        preview_rect: pygame.Rect,
        detection: tuple[int, int],
        left: bool,
    ) -> None:
        frame = self.camera.get_latest()
        if frame is None:
            return
        frame_height, frame_width = frame.frame.shape[:2]
        mid_x = frame_width // 2
        if left:
            x_norm = detection[0] / max(1, mid_x)
            x_pos = preview_rect.left + int(x_norm * (preview_rect.width / 2))
            color = (255, 190, 80)
        else:
            x_norm = detection[0] / max(1, mid_x)
            x_pos = preview_rect.left + int(preview_rect.width / 2 + x_norm * (preview_rect.width / 2))
            color = (160, 220, 120)
        y_norm = detection[1] / max(1, frame_height)
        y_pos = preview_rect.top + int(y_norm * preview_rect.height)
        pygame.draw.circle(surface, color, (x_pos, y_pos), 8, width=2)
