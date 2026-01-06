"""Settings screen placeholder."""

from __future__ import annotations

from typing import Callable

import pygame

from air_hockey.ui.widgets import Button


class SettingsScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.font = pygame.font.SysFont("arial", 28)
        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.back_button = Button(
            rect=pygame.Rect(40, window_size[1] - 80, 140, 44),
            label="Back",
            on_click=self.on_back,
            font=self.font,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_back()
            return
        self.back_button.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((18, 22, 32))
        title_surf = self.title_font.render("Settings", True, (235, 240, 245))
        title_rect = title_surf.get_rect(center=(self.window_size[0] // 2, 120))
        surface.blit(title_surf, title_rect)

        info_surf = self.font.render("Settings placeholder", True, (200, 210, 220))
        info_rect = info_surf.get_rect(center=(self.window_size[0] // 2, 220))
        surface.blit(info_surf, info_rect)

        self.back_button.draw(surface)
