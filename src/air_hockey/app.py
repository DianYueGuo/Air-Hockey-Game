"""Core app loop and screen management."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pygame

from air_hockey.config.io import load_settings
from air_hockey.ui.screens.calibration import CalibrationScreen
from air_hockey.ui.screens.menu import MenuScreen
from air_hockey.ui.screens.pause import PauseScreen
from air_hockey.ui.screens.play import PlayScreen
from air_hockey.ui.screens.settings import SettingsScreen
from air_hockey.engine.windowing import WindowOptions


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
        settings = load_settings()
        self.window_options = WindowOptions(
            webcam_view_mode=settings.webcam_view_mode,
            scoreboard_mode=settings.scoreboard_mode,
            fullscreen=settings.fullscreen,
            display_index=settings.display_index,
        )
        self.window_size = self._resolve_window_size(window_size)
        self.screen = self._create_window(self.window_size)
        self.clock = pygame.time.Clock()
        self.play_screen: PlayScreen | None = None
        self.menu_screen = MenuScreen(
            window_size=self.window_size,
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
        if self.play_screen is not None:
            self.play_screen.stop()
        self.play_screen = PlayScreen(
            window_size=self.window_size,
            on_back=self._show_menu,
            on_pause=self._show_pause,
        )
        self.manager.current = self.play_screen

    def _show_pause(self) -> None:
        if self.play_screen is None:
            return
        background = self.screen.copy()
        self.manager.current = PauseScreen(
            window_size=self.window_size,
            on_continue=self._resume_play,
            on_settings=self._show_settings_from_pause,
            on_calibration=self._show_calibration_from_pause,
            on_restart=self._restart_play,
            on_quit=self._quit_to_menu,
            background=background,
        )

    def _resume_play(self) -> None:
        if self.play_screen is None:
            return
        self.play_screen.start_camera()
        self.play_screen.apply_settings()
        self.manager.current = self.play_screen

    def _restart_play(self) -> None:
        if self.play_screen is not None:
            self.play_screen.stop()
        self.play_screen = PlayScreen(
            window_size=self.window_size,
            on_back=self._show_menu,
            on_pause=self._show_pause,
        )
        self.manager.current = self.play_screen

    def _quit_to_menu(self) -> None:
        if self.play_screen is not None:
            self.play_screen.stop()
            self.play_screen = None
        self.manager.current = self.menu_screen

    def _show_settings_from_pause(self) -> None:
        if self.play_screen is not None:
            self.play_screen.stop_camera()
        self.manager.current = SettingsScreen(
            window_size=self.window_size, on_back=self._show_pause
        )

    def _show_calibration_from_pause(self) -> None:
        if self.play_screen is not None:
            self.play_screen.stop_camera()
        self.manager.current = CalibrationScreen(
            window_size=self.window_size, on_back=self._show_pause
        )

    def _resolve_window_size(self, requested: tuple[int, int]) -> tuple[int, int]:
        if not self.window_options.fullscreen:
            return requested
        display_info = pygame.display.Info()
        return (display_info.current_w, display_info.current_h)

    def _create_window(self, size: tuple[int, int]) -> pygame.Surface:
        flags = pygame.FULLSCREEN if self.window_options.fullscreen else 0
        display_count = pygame.display.get_num_displays()
        display_index = self.window_options.display_index
        if display_index < 0 or display_index >= display_count:
            display_index = 0
        try:
            screen = pygame.display.set_mode(size, flags, display=display_index)
        except TypeError:
            screen = pygame.display.set_mode(size, flags)
        pygame.display.set_caption("Air Hockey")
        return screen

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
