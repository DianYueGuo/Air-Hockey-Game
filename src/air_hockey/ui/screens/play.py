"""Playable field with Box2D physics (no controls yet)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import cv2
import pygame

from air_hockey.config.io import load_calibration, load_settings
from air_hockey.engine.audio import AudioManager
from air_hockey.engine.camera import CameraCapture
from air_hockey.engine.vision import HSV_PRESETS, detect_largest_ball
from air_hockey.engine.physics import PhysicsWorld
from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode, WindowOptions
from air_hockey.game.entities import MalletSpec
from air_hockey.game.field import FieldSpec
from air_hockey.game.themes import ThemeManager
from air_hockey.ui.screens.hud import Hud
from air_hockey.ui.screens.scoreboard import ScoreboardWindow


@dataclass
class RenderConfig:
    pixels_per_meter: float
    table_rect: pygame.Rect


class PlayScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.field = FieldSpec()
        self.mallet_spec = MalletSpec()
        self.audio = AudioManager()
        self.camera = CameraCapture()
        self.camera_active = self.camera.start()
        settings = load_settings()
        self.window_options = WindowOptions(
            webcam_view_mode=settings.webcam_view_mode,
            scoreboard_mode=settings.scoreboard_mode,
            fullscreen=settings.fullscreen,
            display_index=settings.display_index,
        )
        self.hsv_left = HSV_PRESETS.get(settings.hsv_left, HSV_PRESETS["orange"])
        self.hsv_right = HSV_PRESETS.get(settings.hsv_right, HSV_PRESETS["tennis"])
        self.last_detection_left: tuple[int, int] | None = None
        self.last_detection_right: tuple[int, int] | None = None
        self.use_camera_control = True
        self.calibration = load_calibration()
        self.physics = PhysicsWorld(
            self.field,
            on_puck_wall=self.audio.play_wall,
            on_puck_mallet=self.audio.play_mallet,
        )
        self.clock_accumulator = 0.0
        self.fixed_time_step = 1.0 / 120.0
        self.mallet_speed = settings.mallet_speed_limit
        self.score_left = 0
        self.score_right = 0
        self.trail_positions: list[tuple[float, float]] = []
        self.trail_max = 12
        self.theme_manager = ThemeManager(theme_name=settings.theme)
        self.render_config = self._build_render_config()
        self.font = pygame.font.SysFont("arial", 22)
        self.hud = Hud(window_size=window_size, score_color=self.theme_manager.theme.hud_score)
        self.scoreboard_window: ScoreboardWindow | None = None

    def _build_render_config(self) -> RenderConfig:
        table_width_px = int(self.field.width * 400)
        table_height_px = int(self.field.height * 400)
        table_rect = pygame.Rect(0, 0, table_width_px, table_height_px)
        table_rect.center = (self.window_size[0] // 2, self.window_size[1] // 2)
        return RenderConfig(pixels_per_meter=400.0, table_rect=table_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.camera_active:
                self.camera.stop()
            if self.window_options.webcam_view_mode == WebcamViewMode.WINDOW:
                cv2.destroyWindow("Air Hockey Camera")
            if self.scoreboard_window is not None:
                self.scoreboard_window.close()
            self.on_back()

    def update(self, dt: float) -> None:
        self.clock_accumulator += dt
        keys = pygame.key.get_pressed()
        while self.clock_accumulator >= self.fixed_time_step:
            self._update_detection()
            self._update_mallets(keys, self.fixed_time_step)
            self.physics.step(self.fixed_time_step)
            self._check_goal()
            self.clock_accumulator -= self.fixed_time_step
            self._update_trail()
        puck_velocity = self.physics.entities.puck.linearVelocity
        speed = (puck_velocity[0] ** 2 + puck_velocity[1] ** 2) ** 0.5
        self.audio.update_puck_movement(speed)

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 16, 22))
        self._draw_table(surface)
        self._draw_entities(surface)
        if self.window_options.scoreboard_mode == ScoreboardMode.HUD:
            self.hud.render_score(surface, self.score_left, self.score_right)
        else:
            self._render_scoreboard_window(surface)
        self._draw_webcam_overlay(surface)
        hint = self.font.render("ESC to return to menu", True, (180, 190, 205))
        surface.blit(hint, (16, 16))

    def _world_to_screen(self, position: tuple[float, float]) -> tuple[int, int]:
        px = position[0] * self.render_config.pixels_per_meter
        py = position[1] * self.render_config.pixels_per_meter
        center_x, center_y = self.render_config.table_rect.center
        return int(center_x + px), int(center_y + py)

    def _draw_table(self, surface: pygame.Surface) -> None:
        theme = self.theme_manager.theme
        pygame.draw.rect(surface, theme.table_background, self.render_config.table_rect, border_radius=16)
        pygame.draw.rect(surface, theme.table_border, self.render_config.table_rect, width=4, border_radius=16)
        center_x = self.render_config.table_rect.centerx
        pygame.draw.line(
            surface,
            theme.table_center_line,
            (center_x, self.render_config.table_rect.top),
            (center_x, self.render_config.table_rect.bottom),
            width=2,
        )
        goal_width = int(self.field.height * 0.35 * self.render_config.pixels_per_meter)
        goal_y = self.render_config.table_rect.centery - goal_width // 2
        pygame.draw.rect(
            surface,
            (120, 140, 160),
            pygame.Rect(self.render_config.table_rect.left - 6, goal_y, 6, goal_width),
        )
        pygame.draw.rect(
            surface,
            (120, 140, 160),
            pygame.Rect(self.render_config.table_rect.right, goal_y, 6, goal_width),
        )

    def _draw_entities(self, surface: pygame.Surface) -> None:
        puck = self.physics.entities.puck
        mallet_left = self.physics.entities.mallet_left
        mallet_right = self.physics.entities.mallet_right

        self._draw_trail(surface)
        theme = self.theme_manager.theme
        self._draw_circle(surface, puck.position, 0.04, theme.puck)
        self._draw_circle(surface, mallet_left.position, 0.07, theme.mallet_left)
        self._draw_circle(surface, mallet_right.position, 0.07, theme.mallet_right)
        self._draw_detection_marker(surface)

    def _check_goal(self) -> None:
        puck = self.physics.entities.puck
        half_width = self.field.width / 2.0
        if puck.position[0] < -half_width:
            self.score_right += 1
            self.audio.play_goal()
            self._reset_positions()
        elif puck.position[0] > half_width:
            self.score_left += 1
            self.audio.play_goal()
            self._reset_positions()

    def _reset_positions(self) -> None:
        self.physics.entities.puck.position = (0.0, 0.0)
        self.physics.entities.puck.linearVelocity = (0.0, 0.0)
        left_pos = (-self.field.width * 0.25, 0.0)
        right_pos = (self.field.width * 0.25, 0.0)
        self.physics.set_mallet_positions(left_pos, right_pos)
        self.trail_positions.clear()

    def _update_trail(self) -> None:
        puck_pos = self.physics.entities.puck.position
        self.trail_positions.append((puck_pos[0], puck_pos[1]))
        if len(self.trail_positions) > self.trail_max:
            self.trail_positions.pop(0)

    def _draw_trail(self, surface: pygame.Surface) -> None:
        if len(self.trail_positions) < 2:
            return
        base_color = self.theme_manager.theme.trail
        for index, position in enumerate(self.trail_positions[:-1]):
            alpha = (index + 1) / len(self.trail_positions)
            color = (
                int(base_color[0] * alpha),
                int(base_color[1] * alpha),
                int(base_color[2] * alpha),
            )
            self._draw_circle(surface, position, 0.028, color)

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
        if self.window_options.webcam_view_mode == WebcamViewMode.WINDOW:
            preview = frame.frame.copy()
            if self.last_detection_left:
                cv2.circle(preview, self.last_detection_left, 8, (0, 200, 255), 2)
            if self.last_detection_right:
                right_pos = (self.last_detection_right[0] + mid_x, self.last_detection_right[1])
                cv2.circle(preview, right_pos, 8, (120, 255, 120), 2)
            cv2.imshow("Air Hockey Camera", preview)
            cv2.waitKey(1)

    def _draw_detection_marker(self, surface: pygame.Surface) -> None:
        frame = self.camera.get_latest()
        if frame is None:
            return
        frame_height, frame_width = frame.frame.shape[:2]
        mid_x = frame_width // 2

        if self.last_detection_left:
            world_pos = self._map_detection_to_world(
                self.last_detection_left, frame_height, mid_x, left=True
            )
            self._draw_circle(surface, world_pos, 0.03, (255, 190, 80))

        if self.last_detection_right:
            world_pos = self._map_detection_to_world(
                self.last_detection_right, frame_height, mid_x, left=False
            )
            self._draw_circle(surface, world_pos, 0.03, (160, 220, 120))

    def _draw_webcam_overlay(self, surface: pygame.Surface) -> None:
        if self.window_options.webcam_view_mode != WebcamViewMode.OVERLAY:
            return
        frame = self.camera.get_latest()
        if frame is None:
            return
        frame_bgr = frame.frame
        frame_rgb = frame_bgr[:, :, ::-1]
        overlay_width = 240
        overlay_height = int(overlay_width * frame_rgb.shape[0] / frame_rgb.shape[1])
        overlay = pygame.transform.smoothscale(
            pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1)),
            (overlay_width, overlay_height),
        )
        overlay_rect = overlay.get_rect()
        overlay_rect.midbottom = (self.window_size[0] // 2, self.window_size[1] - 10)
        surface.blit(overlay, overlay_rect)

    def _render_scoreboard_window(self, surface: pygame.Surface) -> None:
        if self.scoreboard_window is None:
            self.scoreboard_window = ScoreboardWindow()
        if not self.scoreboard_window.available:
            self.hud.render_score(surface, self.score_left, self.score_right)
            return
        self.scoreboard_window.render(self.score_left, self.score_right)

    def _update_mallets(self, keys: pygame.key.ScancodeWrapper, dt: float) -> None:
        left_pos = self._move_mallet(
            keys,
            self.physics.entities.mallet_left.position,
            dt,
            left=True,
        )
        right_pos = self._move_mallet(
            keys,
            self.physics.entities.mallet_right.position,
            dt,
            left=False,
        )
        if self.use_camera_control:
            left_cam = self._camera_position(left=True)
            right_cam = self._camera_position(left=False)
            if left_cam is not None:
                left_pos = left_cam
            if right_cam is not None:
                right_pos = right_cam
        self.physics.set_mallet_positions(left_pos, right_pos)

    def _move_mallet(
        self,
        keys: pygame.key.ScancodeWrapper,
        current_pos: tuple[float, float],
        dt: float,
        left: bool,
    ) -> tuple[float, float]:
        if left:
            dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.mallet_speed * dt
            dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.mallet_speed * dt
        else:
            dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.mallet_speed * dt
            dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.mallet_speed * dt

        x = current_pos[0] + dx
        y = current_pos[1] + dy

        return self._clamp_mallet_position((x, y), left=left)

    def _clamp_mallet_position(self, position: tuple[float, float], left: bool) -> tuple[float, float]:
        x, y = position
        half_width = self.field.width / 2.0
        half_height = self.field.height / 2.0
        radius = self.mallet_spec.radius

        if left:
            x_min = -half_width + radius
            x_max = -radius
        else:
            x_min = radius
            x_max = half_width - radius

        y_min = -half_height + radius
        y_max = half_height - radius

        x = max(x_min, min(x, x_max))
        y = max(y_min, min(y, y_max))

        return (x, y)

    def _camera_position(self, left: bool) -> tuple[float, float] | None:
        frame = self.camera.get_latest()
        if frame is None:
            return None
        frame_height, frame_width = frame.frame.shape[:2]
        mid_x = frame_width // 2
        if left:
            detection = self.last_detection_left
            if detection is None:
                return None
            return self._map_detection_to_world(detection, frame_height, mid_x, left=True)
        detection = self.last_detection_right
        if detection is None:
            return None
        return self._map_detection_to_world(detection, frame_height, mid_x, left=False)

    def _map_detection_to_world(
        self, detection: tuple[int, int], frame_height: int, half_width_px: int, left: bool
    ) -> tuple[float, float]:
        if left:
            calib = self.calibration.left
        else:
            calib = self.calibration.right

        x_norm = self._normalize_axis(
            detection[0],
            calib.cam_x_min,
            calib.cam_x_max,
            0.0,
            float(half_width_px),
        )
        y_norm = self._normalize_axis(
            detection[1],
            calib.cam_y_min,
            calib.cam_y_max,
            0.0,
            float(frame_height),
        )
        half_width = self.field.width / 2.0
        half_height = self.field.height / 2.0
        if left:
            world_x = (-half_width) + x_norm * half_width
        else:
            world_x = 0.0 + x_norm * half_width
        world_y = (-half_height) + y_norm * self.field.height
        return self._clamp_mallet_position((world_x, world_y), left=left)

    @staticmethod
    def _normalize_axis(
        value: float,
        min_val: float | None,
        max_val: float | None,
        fallback_min: float,
        fallback_max: float,
    ) -> float:
        if min_val is None or max_val is None or max_val == min_val:
            min_val = fallback_min
            max_val = fallback_max
        norm = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, norm))

    def _draw_circle(
        self, surface: pygame.Surface, position: tuple[float, float], radius: float, color: tuple[int, int, int]
    ) -> None:
        screen_pos = self._world_to_screen(position)
        radius_px = int(radius * self.render_config.pixels_per_meter)
        pygame.draw.circle(surface, color, screen_pos, radius_px)
        pygame.draw.circle(surface, (20, 30, 40), screen_pos, radius_px, width=2)
