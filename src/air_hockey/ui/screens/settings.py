"""Settings screen placeholder."""

from __future__ import annotations

from typing import Callable

import pygame

from air_hockey.config.io import load_settings, save_settings
from air_hockey.engine.windowing import ScoreboardMode, WebcamViewMode
from air_hockey.ui.widgets import Button


class SettingsScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.font = pygame.font.SysFont("arial", 28)
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.small_font = pygame.font.SysFont("arial", 20)
        self.settings = load_settings()
        self.message = ""
        self.back_button = Button(
            rect=pygame.Rect(40, window_size[1] - 80, 140, 44),
            label="Back",
            on_click=self._exit,
            font=self.font,
        )
        self.toggle_webcam_button = Button(
            rect=pygame.Rect(80, 220, 320, 44),
            label="Webcam View: OVERLAY",
            on_click=self._toggle_webcam_view,
            font=self.font,
        )
        self.toggle_scoreboard_button = Button(
            rect=pygame.Rect(80, 280, 320, 44),
            label="Scoreboard: HUD",
            on_click=self._toggle_scoreboard,
            font=self.font,
        )

    def _exit(self) -> None:
        save_settings(self.settings)
        self.on_back()

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

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._exit()
            return
        self.back_button.handle_event(event)
        self.toggle_webcam_button.handle_event(event)
        self.toggle_scoreboard_button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((18, 22, 32))
        title_surf = self.title_font.render("Settings", True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 120))
        surface.blit(title_surf, title_rect)

        self._refresh_labels()
        self.toggle_webcam_button.draw(surface)
        self.toggle_scoreboard_button.draw(surface)

        if self.message:
            msg_surf = self.small_font.render(self.message, True, (180, 190, 200))
            msg_rect = msg_surf.get_rect(center=(self.window_size[0] // 2, 360))
            surface.blit(msg_surf, msg_rect)

        self.back_button.draw(surface)

    def _refresh_labels(self) -> None:
        self.toggle_webcam_button.label = (
            f"Webcam View: {self.settings.webcam_view_mode.value.upper()}"
        )
        self.toggle_scoreboard_button.label = (
            f"Scoreboard: {self.settings.scoreboard_mode.value.upper()}"
        )
