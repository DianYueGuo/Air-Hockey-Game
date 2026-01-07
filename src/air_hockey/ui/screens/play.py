"""Playable field with Box2D physics (no controls yet)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import cv2
import pygame

from air_hockey.config.io import load_calibration, load_settings
from air_hockey.engine.audio import AudioManager
from air_hockey.engine.camera import CameraCapture
from air_hockey.engine.vision import (
    HSV_PRESETS,
    MotionMasker,
    detect_largest_ball,
    detect_largest_ball_masked,
    resolve_hsv_range,
)
from air_hockey.engine.physics import PhysicsWorld
from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode, WindowOptions
from air_hockey.game.entities import MalletSpec
from air_hockey.game.field import FieldSpec
from air_hockey.game.themes import ThemeManager
from air_hockey.ui.fonts import get_font
from air_hockey.ui.screens.hud import Hud
from air_hockey.ui.screens.scoreboard import ScoreboardWindow


@dataclass
class RenderConfig:
    pixels_per_meter: float
    table_rect: pygame.Rect


class PlayScreen:
    def __init__(
        self,
        window_size: tuple[int, int],
        on_back: Callable[[], None],
        on_pause: Callable[[], None],
    ) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.on_pause = on_pause
        self.field = FieldSpec()
        self.mallet_spec = MalletSpec()
        settings = load_settings()
        self.audio = AudioManager(sound_pack=settings.sound_pack)
        self.camera = CameraCapture()
        self.camera_active = False
        self.window_options = WindowOptions(
            webcam_view_mode=settings.webcam_view_mode,
            scoreboard_mode=settings.scoreboard_mode,
            fullscreen=settings.fullscreen,
            display_index=settings.display_index,
        )
        self.settings = settings
        if settings.force_same_hsv:
            self.hsv_left = resolve_hsv_range(settings.hsv_left, settings.hsv_left_range)
            self.hsv_right = self.hsv_left
        else:
            self.hsv_left = resolve_hsv_range(settings.hsv_left, settings.hsv_left_range)
            self.hsv_right = resolve_hsv_range(settings.hsv_right, settings.hsv_right_range)
        self.motion_mask_mode = settings.motion_mask_mode
        self.motion_masker = MotionMasker() if self.motion_mask_mode == "mog2" else None
        self.last_detection_left: tuple[int, int] | None = None
        self.last_detection_right: tuple[int, int] | None = None
        self.use_camera_control = True
        self.smoothing = settings.smoothing
        self.smoothed_left: tuple[float, float] | None = None
        self.smoothed_right: tuple[float, float] | None = None
        self.calibration = load_calibration()
        self.physics = PhysicsWorld(
            self.field,
            on_puck_wall=self.audio.play_wall,
            on_puck_mallet=self.audio.play_mallet,
            puck_restitution=settings.puck_restitution,
            puck_damping=settings.puck_damping,
            max_puck_speed=settings.max_puck_speed,
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
        self.font = get_font(22)
        self.hud = Hud(window_size=window_size, score_color=self.theme_manager.theme.hud_score)
        self.scoreboard_window: ScoreboardWindow | None = None
        self.start_camera()

    def _build_render_config(self) -> RenderConfig:
        table_width_px = int(self.field.width * 400)
        table_height_px = int(self.field.height * 400)
        table_rect = pygame.Rect(0, 0, table_width_px, table_height_px)
        table_rect.center = (self.window_size[0] // 2, self.window_size[1] // 2)
        return RenderConfig(pixels_per_meter=400.0, table_rect=table_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_pause()

    def start_camera(self) -> None:
        if not self.camera_active:
            self.camera_active = self.camera.start()

    def stop_camera(self) -> None:
        if self.camera_active:
            self.camera.stop()
            self.camera_active = False
        if self.window_options.webcam_view_mode == WebcamViewMode.WINDOW:
            cv2.destroyWindow("Air Hockey Camera")

    def stop(self) -> None:
        self.stop_camera()
        if self.scoreboard_window is not None:
            self.scoreboard_window.close()

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

    def apply_settings(self) -> None:
        settings = load_settings()
        old_webcam_mode = self.window_options.webcam_view_mode
        old_scoreboard_mode = self.window_options.scoreboard_mode
        old_sound_pack = self.settings.sound_pack

        self.window_options = WindowOptions(
            webcam_view_mode=settings.webcam_view_mode,
            scoreboard_mode=settings.scoreboard_mode,
            fullscreen=settings.fullscreen,
            display_index=settings.display_index,
        )
        self.theme_manager = ThemeManager(theme_name=settings.theme)
        self.hud.score_color = self.theme_manager.theme.hud_score
        self.mallet_speed = settings.mallet_speed_limit
        self.smoothing = settings.smoothing
        self.hsv_left = resolve_hsv_range(settings.hsv_left, settings.hsv_left_range)
        self.hsv_right = resolve_hsv_range(settings.hsv_right, settings.hsv_right_range)
        self.physics.update_puck_settings(
            restitution=settings.puck_restitution,
            damping=settings.puck_damping,
            max_speed=settings.max_puck_speed,
        )

        if settings.force_same_hsv:
            self.hsv_left = resolve_hsv_range(settings.hsv_left, settings.hsv_left_range)
            self.hsv_right = self.hsv_left
        else:
            self.hsv_left = resolve_hsv_range(settings.hsv_left, settings.hsv_left_range)
            self.hsv_right = resolve_hsv_range(settings.hsv_right, settings.hsv_right_range)

        if old_sound_pack != settings.sound_pack:
            self.audio.reload(settings.sound_pack)

        if self.motion_mask_mode != settings.motion_mask_mode:
            self.motion_mask_mode = settings.motion_mask_mode
            self.motion_masker = MotionMasker() if self.motion_mask_mode == "mog2" else None

        if old_webcam_mode == WebcamViewMode.WINDOW and settings.webcam_view_mode != WebcamViewMode.WINDOW:
            cv2.destroyWindow("Air Hockey Camera")

        if old_scoreboard_mode == ScoreboardMode.WINDOW and settings.scoreboard_mode == ScoreboardMode.HUD:
            if self.scoreboard_window is not None:
                self.scoreboard_window.close()
                self.scoreboard_window = None

        self.settings = settings

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
        self.physics.set_mallet_positions(
            left_pos,
            right_pos,
            time_step=dt,
            max_speed=self.mallet_speed,
        )
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
        frame_bgr = cv2.flip(frame.frame, 1)
        frame_height, frame_width = frame_bgr.shape[:2]
        mid_x = frame_width // 2

        left_frame = frame_bgr[:, :mid_x]
        right_frame = frame_bgr[:, mid_x:]

        if self.motion_masker:
            motion_mask = self.motion_masker.apply(frame_bgr)
            left_motion = motion_mask[:, :mid_x]
            right_motion = motion_mask[:, mid_x:]
            left_result = detect_largest_ball_masked(left_frame, self.hsv_left, left_motion)
            right_result = detect_largest_ball_masked(right_frame, self.hsv_right, right_motion)
        else:
            left_result = detect_largest_ball(left_frame, self.hsv_left)
            right_result = detect_largest_ball(right_frame, self.hsv_right)

        self.last_detection_left = left_result.center
        self.last_detection_right = right_result.center
        if self.window_options.webcam_view_mode == WebcamViewMode.WINDOW:
            preview = frame_bgr.copy()
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
        frame_bgr = cv2.flip(frame.frame, 1)
        frame_height, frame_width = frame_bgr.shape[:2]
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
        frame_bgr = cv2.flip(frame.frame, 1)
        frame_height, frame_width = frame_bgr.shape[:2]
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
        self._draw_overlay_markers(surface, overlay_rect, frame_width, frame_height)

    def _draw_overlay_markers(
        self,
        surface: pygame.Surface,
        overlay_rect: pygame.Rect,
        frame_width: int,
        frame_height: int,
    ) -> None:
        if frame_width <= 0 or frame_height <= 0:
            return
        mid_x = frame_width // 2
        if self.last_detection_left:
            x_norm = self.last_detection_left[0] / max(1, mid_x)
            y_norm = self.last_detection_left[1] / max(1, frame_height)
            x_pos = overlay_rect.left + int(x_norm * (overlay_rect.width / 2))
            y_pos = overlay_rect.top + int(y_norm * overlay_rect.height)
            pygame.draw.circle(surface, (255, 190, 80), (x_pos, y_pos), 6, width=2)
        if self.last_detection_right:
            x_norm = self.last_detection_right[0] / max(1, mid_x)
            y_norm = self.last_detection_right[1] / max(1, frame_height)
            x_pos = overlay_rect.left + int(overlay_rect.width / 2 + x_norm * (overlay_rect.width / 2))
            y_pos = overlay_rect.top + int(y_norm * overlay_rect.height)
            pygame.draw.circle(surface, (160, 220, 120), (x_pos, y_pos), 6, width=2)

    def _render_scoreboard_window(self, surface: pygame.Surface) -> None:
        if self.scoreboard_window is None:
            self.scoreboard_window = ScoreboardWindow()
        if not self.scoreboard_window.available:
            self.hud.render_score(surface, self.score_left, self.score_right)
            return
        rendered = self.scoreboard_window.render(self.score_left, self.score_right)
        if not rendered:
            self.scoreboard_window.available = False
            self.hud.render_score(surface, self.score_left, self.score_right)

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
        self.physics.set_mallet_positions(
            left_pos,
            right_pos,
            time_step=self.fixed_time_step,
            teleport=True,
        )

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
                return self.smoothed_left
            world_pos = self._map_detection_to_world(detection, frame_height, mid_x, left=True)
            self.smoothed_left = self._apply_smoothing(self.smoothed_left, world_pos)
            return self.smoothed_left
        detection = self.last_detection_right
        if detection is None:
            return self.smoothed_right
        world_pos = self._map_detection_to_world(detection, frame_height, mid_x, left=False)
        self.smoothed_right = self._apply_smoothing(self.smoothed_right, world_pos)
        return self.smoothed_right

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
        if left:
            x_norm = 1.0 - x_norm
        half_width = self.field.width / 2.0
        half_height = self.field.height / 2.0
        if left:
            world_x = (-half_width) + x_norm * half_width
        else:
            world_x = 0.0 + x_norm * half_width
        world_y = (-half_height) + y_norm * self.field.height
        return self._clamp_mallet_position((world_x, world_y), left=left)

    def _apply_smoothing(
        self, current: tuple[float, float] | None, target: tuple[float, float]
    ) -> tuple[float, float]:
        if current is None or self.smoothing <= 0.0:
            return target
        alpha = max(0.0, min(1.0, self.smoothing))
        x = alpha * target[0] + (1.0 - alpha) * current[0]
        y = alpha * target[1] + (1.0 - alpha) * current[1]
        return (x, y)

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
