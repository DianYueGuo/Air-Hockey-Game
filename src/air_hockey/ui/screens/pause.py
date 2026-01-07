"""Pause menu screen."""

from __future__ import annotations

from typing import Callable

import pygame

from air_hockey.ui.fonts import get_font
from air_hockey.ui.widgets import Button


class PauseScreen:
    def __init__(
        self,
        window_size: tuple[int, int],
        on_continue: Callable[[], None],
        on_settings: Callable[[], None],
        on_calibration: Callable[[], None],
        on_restart: Callable[[], None],
        on_quit: Callable[[], None],
        background: pygame.Surface | None = None,
    ) -> None:
        self.window_size = window_size
        self.on_continue = on_continue
        self.on_settings = on_settings
        self.on_calibration = on_calibration
        self.on_restart = on_restart
        self.on_quit = on_quit
        self.background = background
        self.font = get_font(28)
        self.title_font = get_font(40, bold=True)
        self.buttons = self._build_buttons()

    def _build_buttons(self) -> list[Button]:
        labels: list[tuple[str, Callable[[], None]]] = [
            ("Continue", self.on_continue),
            ("Settings", self.on_settings),
            ("Calibration", self.on_calibration),
            ("Restart", self.on_restart),
            ("Quit", self.on_quit),
        ]
        button_width = 260
        button_height = 50
        spacing = 14
        total_height = len(labels) * button_height + (len(labels) - 1) * spacing
        start_y = (self.window_size[1] - total_height) // 2 + 20
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

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_continue()
            return
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        if self.background:
            surface.blit(self.background, (0, 0))
            overlay = pygame.Surface(self.window_size, pygame.SRCALPHA)
            overlay.fill((10, 12, 18, 180))
            surface.blit(overlay, (0, 0))
        else:
            surface.fill((12, 18, 26))
        title_surf = self.title_font.render("Paused", True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 120))
        surface.blit(title_surf, title_rect)
        for button in self.buttons:
            button.draw(surface)
