"""Main menu screen."""

from __future__ import annotations

from typing import Callable

import pygame

from air_hockey.ui.fonts import get_font
from air_hockey.ui.widgets import Button


class MenuScreen:
    def __init__(
        self,
        window_size: tuple[int, int],
        on_play: Callable[[], None] | None = None,
        on_settings: Callable[[], None] | None = None,
        on_calibration: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
    ) -> None:
        self.window_size = window_size
        self.font = get_font(28)
        self.title_font = get_font(44, bold=True)
        self.message = ""
        self.on_play = on_play
        self.on_settings = on_settings
        self.on_calibration = on_calibration
        self.on_quit = on_quit
        self.buttons = self._build_buttons()

    def _build_buttons(self) -> list[Button]:
        labels: list[tuple[str, Callable[[], None]]] = [
            ("Play", self._on_play),
            ("Settings", self._on_settings),
            ("Calibration", self._on_calibration),
            ("Quit", self._on_quit),
        ]
        button_width = 260
        button_height = 52
        spacing = 16
        total_height = len(labels) * button_height + (len(labels) - 1) * spacing
        start_y = (self.window_size[1] - total_height) // 2 + 40
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

    def _set_message(self, text: str) -> None:
        self.message = text

    def _on_play(self) -> None:
        if self.on_play is None:
            self._set_message("Play selected (placeholder)")
            return
        self.on_play()

    def _on_settings(self) -> None:
        if self.on_settings is None:
            self._set_message("Settings selected (placeholder)")
            return
        self.on_settings()

    def _on_calibration(self) -> None:
        if self.on_calibration is None:
            self._set_message("Calibration selected (placeholder)")
            return
        self.on_calibration()

    def _on_quit(self) -> None:
        if self.on_quit is None:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        self.on_quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        for button in self.buttons:
            button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 20, 30))
        title_surf = self.title_font.render("Air Hockey", True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 120))
        surface.blit(title_surf, title_rect)

        for button in self.buttons:
            button.draw(surface)

        if self.message:
            message_surf = self.font.render(self.message, True, (200, 210, 220))
            message_rect = message_surf.get_rect(center=(self.window_size[0] // 2, 420))
            surface.blit(message_surf, message_rect)
