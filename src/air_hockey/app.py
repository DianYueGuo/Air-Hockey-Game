"""Core app loop and screen management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pygame

from air_hockey.ui.screens.calibration import CalibrationScreen
from air_hockey.ui.screens.menu import MenuScreen
from air_hockey.ui.screens.play import PlayScreen
from air_hockey.ui.screens.settings import SettingsScreen


class Screen(Protocol):
    def handle_event(self, event: pygame.event.Event) -> None:
        ...

    def update(self, dt: float) -> None:
        ...

    def render(self, surface: pygame.Surface) -> None:
        ...


@dataclass
class ScreenManager:
    current: Screen

    def handle_event(self, event: pygame.event.Event) -> None:
        self.current.handle_event(event)

    def update(self, dt: float) -> None:
        self.current.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.current.render(surface)


class PlaceholderScreen:
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 20, 30))


class App:
    def __init__(self, window_size: tuple[int, int]) -> None:
        self.window_size = window_size
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption("Air Hockey")
        self.clock = pygame.time.Clock()
        self.menu_screen = MenuScreen(
            window_size=window_size,
            on_play=self._show_play,
            on_settings=self._show_settings,
            on_calibration=self._show_calibration,
        )
        self.manager = ScreenManager(current=self.menu_screen)

    def _show_menu(self) -> None:
        self.manager.current = self.menu_screen

    def _show_settings(self) -> None:
        self.manager.current = SettingsScreen(
            window_size=self.window_size, on_back=self._show_menu
        )

    def _show_calibration(self) -> None:
        self.manager.current = CalibrationScreen(
            window_size=self.window_size, on_back=self._show_menu
        )

    def _show_play(self) -> None:
        self.manager.current = PlayScreen(
            window_size=self.window_size, on_back=self._show_menu
        )

    def run(self) -> int:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.manager.handle_event(event)

            dt = self.clock.get_time() / 1000.0
            self.manager.update(dt)
            self.manager.render(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

        return 0
