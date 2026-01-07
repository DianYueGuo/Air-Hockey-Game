"""Settings screen with basic toggles and tuning panels."""

from __future__ import annotations

from typing import Callable

import pygame

from air_hockey.config.io import load_settings, save_settings
from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode
from air_hockey.ui.fonts import get_font
from air_hockey.ui.widgets import Button


class SettingsScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.font = get_font(28)
        self.title_font = get_font(40, bold=True)
        self.small_font = get_font(20)
        self.settings = load_settings()
        self.message = ""
        self.mode = "main"
        self.back_button = Button(
            rect=pygame.Rect(40, window_size[1] - 80, 140, 44),
            label="Back",
            on_click=self._exit,
            font=self.font,
        )
        self.main_buttons = self._build_main_buttons()
        self.physics_buttons = self._build_physics_buttons()
        self.vision_buttons = self._build_vision_buttons()
        self.physics_back_button = Button(
            rect=pygame.Rect(window_size[0] - 220, window_size[1] - 80, 180, 44),
            label="Back to Settings",
            on_click=self._enter_main,
            font=self.font,
        )
        self.vision_back_button = Button(
            rect=pygame.Rect(window_size[0] - 220, window_size[1] - 80, 180, 44),
            label="Back to Settings",
            on_click=self._enter_main,
            font=self.font,
        )

    def _build_main_buttons(self) -> list[Button]:
        labels: list[tuple[str, Callable[[], None]]] = [
            ("Webcam View", self._toggle_webcam_view),
            ("Scoreboard", self._toggle_scoreboard),
            ("Theme", self._toggle_theme),
            ("Sound Pack", self._toggle_sound_pack),
            ("Fullscreen", self._toggle_fullscreen),
            ("Display", self._cycle_display),
            ("Vision Tuning", self._enter_vision),
            ("Physics Tuning", self._enter_physics),
        ]
        button_width = 320
        button_height = 44
        spacing = 10
        total_height = len(labels) * button_height + (len(labels) - 1) * spacing
        start_y = (self.window_size[1] - total_height) // 2
        start_x = (self.window_size[0] - button_width) // 2

        buttons: list[Button] = []
        for index, (label, handler) in enumerate(labels):
            rect = pygame.Rect(
                start_x,
                start_y + index * (button_height + spacing),
                button_width,
                button_height,
            )
            buttons.append(Button(rect=rect, label=label, on_click=handler, font=self.font))
        return buttons

    def _build_physics_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        button_width = 120
        button_height = 40
        spacing_y = 52
        left_x = self.window_size[0] // 2 - 140
        right_x = self.window_size[0] // 2 + 20
        start_y = 200

        def add_row(index: int, on_minus: Callable[[], None], on_plus: Callable[[], None]) -> None:
            y = start_y + index * spacing_y
            buttons.append(
                Button(
                    rect=pygame.Rect(left_x, y, button_width, button_height),
                    label="-",
                    on_click=on_minus,
                    font=self.font,
                )
            )
            buttons.append(
                Button(
                    rect=pygame.Rect(right_x, y, button_width, button_height),
                    label="+",
                    on_click=on_plus,
                    font=self.font,
                )
            )

        add_row(0, self._dec_puck_restitution, self._inc_puck_restitution)
        add_row(1, self._dec_puck_damping, self._inc_puck_damping)
        add_row(2, self._dec_max_speed, self._inc_max_speed)
        add_row(3, self._dec_mallet_speed, self._inc_mallet_speed)

        return buttons

    def _build_vision_buttons(self) -> list[Button]:
        buttons: list[Button] = []
        button_width = 120
        button_height = 40
        left_x = self.window_size[0] // 2 - 140
        right_x = self.window_size[0] // 2 + 20
        start_y = 200

        def add_row(index: int, on_minus: Callable[[], None], on_plus: Callable[[], None]) -> None:
            y = start_y + index * 52
            buttons.append(
                Button(
                    rect=pygame.Rect(left_x, y, button_width, button_height),
                    label="-",
                    on_click=on_minus,
                    font=self.font,
                )
            )
            buttons.append(
                Button(
                    rect=pygame.Rect(right_x, y, button_width, button_height),
                    label="+",
                    on_click=on_plus,
                    font=self.font,
                )
            )

        add_row(0, self._dec_smoothing, self._inc_smoothing)
        add_row(1, self._dec_detection_scale, self._inc_detection_scale)
        add_row(2, self._dec_max_jump, self._inc_max_jump)
        add_row(3, self._dec_hand_rate, self._inc_hand_rate)

        return buttons

    def _exit(self) -> None:
        save_settings(self.settings)
        self.on_back()

    def _enter_physics(self) -> None:
        self.mode = "physics"
        self.message = ""

    def _enter_vision(self) -> None:
        self.mode = "vision"
        self.message = ""

    def _enter_main(self) -> None:
        self.mode = "main"
        self.message = ""

    def _toggle_webcam_view(self) -> None:
        current = self.settings.webcam_view_mode
        if current == WebcamViewMode.HIDDEN:
            self.settings.webcam_view_mode = WebcamViewMode.OVERLAY
        elif current == WebcamViewMode.OVERLAY:
            self.settings.webcam_view_mode = WebcamViewMode.WINDOW
        else:
            self.settings.webcam_view_mode = WebcamViewMode.HIDDEN
        self.message = "Webcam view updated."

    def _toggle_scoreboard(self) -> None:
        if self.settings.scoreboard_mode == ScoreboardMode.HUD:
            self.settings.scoreboard_mode = ScoreboardMode.WINDOW
        else:
            self.settings.scoreboard_mode = ScoreboardMode.HUD
        self.message = "Scoreboard mode updated."

    def _toggle_theme(self) -> None:
        self.settings.theme = "retro" if self.settings.theme == "default" else "default"
        self.message = "Theme updated."

    def _toggle_sound_pack(self) -> None:
        self.settings.sound_pack = "retro" if self.settings.sound_pack == "default" else "default"
        self.message = "Sound pack updated."

    def _toggle_fullscreen(self) -> None:
        self.settings.fullscreen = not self.settings.fullscreen
        self.message = "Fullscreen toggled. Restart app to apply."

    def _cycle_display(self) -> None:
        display_count = pygame.display.get_num_displays() or 1
        self.settings.display_index = (self.settings.display_index + 1) % display_count
        self.message = "Display index updated. Restart app to apply."

    def _inc_puck_restitution(self) -> None:
        self.settings.puck_restitution = self._clamp(
            self.settings.puck_restitution + 0.05, 0.0, 1.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _dec_puck_restitution(self) -> None:
        self.settings.puck_restitution = self._clamp(
            self.settings.puck_restitution - 0.05, 0.0, 1.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _inc_puck_damping(self) -> None:
        self.settings.puck_damping = self._clamp(
            self.settings.puck_damping + 0.05, 0.0, 2.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _dec_puck_damping(self) -> None:
        self.settings.puck_damping = self._clamp(
            self.settings.puck_damping - 0.05, 0.0, 2.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _inc_max_speed(self) -> None:
        self.settings.max_puck_speed = self._clamp(
            self.settings.max_puck_speed + 0.2, 0.5, 8.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _dec_max_speed(self) -> None:
        self.settings.max_puck_speed = self._clamp(
            self.settings.max_puck_speed - 0.2, 0.5, 8.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _inc_mallet_speed(self) -> None:
        self.settings.mallet_speed_limit = self._clamp(
            self.settings.mallet_speed_limit + 0.1, 0.5, 3.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _dec_mallet_speed(self) -> None:
        self.settings.mallet_speed_limit = self._clamp(
            self.settings.mallet_speed_limit - 0.1, 0.5, 3.0
        )
        self.message = "Physics updated. Re-enter Play."

    def _inc_smoothing(self) -> None:
        self.settings.smoothing = self._clamp(self.settings.smoothing + 0.05, 0.0, 1.0)
        self.message = "Vision updated. Re-enter Play."

    def _dec_smoothing(self) -> None:
        self.settings.smoothing = self._clamp(self.settings.smoothing - 0.05, 0.0, 1.0)
        self.message = "Vision updated. Re-enter Play."

    def _inc_detection_scale(self) -> None:
        self.settings.detection_scale = self._clamp(self.settings.detection_scale + 0.1, 0.3, 1.0)
        self.message = "Vision updated. Re-enter Play."

    def _dec_detection_scale(self) -> None:
        self.settings.detection_scale = self._clamp(self.settings.detection_scale - 0.1, 0.3, 1.0)
        self.message = "Vision updated. Re-enter Play."

    def _inc_max_jump(self) -> None:
        self.settings.max_jump_px = self._clamp(self.settings.max_jump_px + 10.0, 20.0, 300.0)
        self.message = "Vision updated. Re-enter Play."

    def _dec_max_jump(self) -> None:
        self.settings.max_jump_px = self._clamp(self.settings.max_jump_px - 10.0, 20.0, 300.0)
        self.message = "Vision updated. Re-enter Play."

    def _inc_hand_rate(self) -> None:
        self.settings.hand_process_every = int(
            self._clamp(self.settings.hand_process_every + 1, 1.0, 5.0)
        )
        self.message = "Vision updated. Re-enter Play."

    def _dec_hand_rate(self) -> None:
        self.settings.hand_process_every = int(
            self._clamp(self.settings.hand_process_every - 1, 1.0, 5.0)
        )
        self.message = "Vision updated. Re-enter Play."

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._exit()
                return
            if event.key == pygame.K_BACKSPACE and self.mode != "main":
                self._enter_main()
                return
        self.back_button.handle_event(event)
        if self.mode == "main":
            for button in self.main_buttons:
                button.handle_event(event)
        elif self.mode == "physics":
            for button in self.physics_buttons:
                button.handle_event(event)
            self.physics_back_button.handle_event(event)
        else:
            for button in self.vision_buttons:
                button.handle_event(event)
            self.vision_back_button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((18, 22, 32))
        title = "Settings"
        if self.mode == "physics":
            title = "Physics Tuning"
        elif self.mode == "vision":
            title = "Vision Tuning"
        title_surf = self.title_font.render(title, True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 110))
        surface.blit(title_surf, title_rect)

        if self.mode == "main":
            self._refresh_main_labels()
            for button in self.main_buttons:
                button.draw(surface)
            if self.message:
                msg_surf = self.small_font.render(self.message, True, (180, 190, 200))
                msg_rect = msg_surf.get_rect(center=(self.window_size[0] // 2, 420))
                surface.blit(msg_surf, msg_rect)
        elif self.mode == "physics":
            self._draw_physics_values(surface)
            for button in self.physics_buttons:
                button.draw(surface)
            if self.message:
                msg_surf = self.small_font.render(self.message, True, (180, 190, 200))
                msg_rect = msg_surf.get_rect(center=(self.window_size[0] // 2, 430))
                surface.blit(msg_surf, msg_rect)
            self.physics_back_button.draw(surface)
        else:
            self._draw_vision_values(surface)
            for button in self.vision_buttons:
                button.draw(surface)
            if self.message:
                msg_surf = self.small_font.render(self.message, True, (180, 190, 200))
                msg_rect = msg_surf.get_rect(center=(self.window_size[0] // 2, 380))
                surface.blit(msg_surf, msg_rect)
            self.vision_back_button.draw(surface)

        self.back_button.draw(surface)

    def _refresh_main_labels(self) -> None:
        labels = {
            "Webcam View": f"Webcam View: {self.settings.webcam_view_mode.value.upper()}",
            "Scoreboard": f"Scoreboard: {self.settings.scoreboard_mode.value.upper()}",
            "Theme": f"Theme: {self.settings.theme.upper()}",
            "Sound Pack": f"Sound Pack: {self.settings.sound_pack.upper()}",
            "Fullscreen": f"Fullscreen: {'ON' if self.settings.fullscreen else 'OFF'}",
            "Display": f"Display: {self.settings.display_index}",
            "Vision Tuning": "Vision Tuning",
            "Physics Tuning": "Physics Tuning",
        }
        for button in self.main_buttons:
            key = button.label.split(":")[0]
            button.label = labels.get(key, button.label)

    def _draw_physics_values(self, surface: pygame.Surface) -> None:
        lines = [
            f"Puck Restitution: {self.settings.puck_restitution:.2f}",
            f"Puck Damping: {self.settings.puck_damping:.2f}",
            f"Max Puck Speed: {self.settings.max_puck_speed:.2f}",
            f"Mallet Speed: {self.settings.mallet_speed_limit:.2f}",
        ]
        start_y = 170
        for index, line in enumerate(lines):
            surf = self.small_font.render(line, True, (200, 210, 220))
            rect = surf.get_rect(center=(self.window_size[0] // 2, start_y + index * 52))
            surface.blit(surf, rect)

    def _draw_vision_values(self, surface: pygame.Surface) -> None:
        lines = [
            f"Smoothing: {self.settings.smoothing:.2f}",
            f"Detection Scale: {self.settings.detection_scale:.2f}",
            f"Max Jump (px): {self.settings.max_jump_px:.0f}",
            f"Process Every: {self.settings.hand_process_every} frame(s)",
        ]
        start_y = 150
        for index, line in enumerate(lines):
            surf = self.small_font.render(line, True, (200, 210, 220))
            rect = surf.get_rect(center=(self.window_size[0] // 2, start_y + index * 44))
            surface.blit(surf, rect)

    @staticmethod
    def _clamp(value: float, min_value: float, max_value: float) -> float:
        return max(min_value, min(max_value, value))
