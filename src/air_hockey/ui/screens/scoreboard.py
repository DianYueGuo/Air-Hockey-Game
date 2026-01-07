"""Separate scoreboard window."""

from __future__ import annotations

from typing import Any

import pygame


class ScoreboardWindow:
    def __init__(self, window_size: tuple[int, int] = (360, 160)) -> None:
        self.window_size = window_size
        self.available = False
        self._window: Any | None = None
        self._renderer: Any | None = None
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        try:
            import pygame._sdl2.video as sdl2
        except ImportError:
            return
        self._window = sdl2.Window("Air Hockey Scoreboard", size=window_size)
        self._renderer = sdl2.Renderer(self._window)
        self.available = True

    def render(self, score_left: int, score_right: int) -> None:
        if not self.available or self._renderer is None:
            return
        score_text = f"{score_left}   :   {score_right}"
        score_surf = self.font.render(score_text, True, (235, 240, 245))
        score_rect = score_surf.get_rect(center=(self.window_size[0] // 2, self.window_size[1] // 2))

        self._renderer.clear()
        texture = self._renderer.texture_from_surface(score_surf)
        try:
            self._renderer.blit(texture, score_rect)
        except AttributeError:
            self._renderer.copy(texture, score_rect)
        self._renderer.present()

    def close(self) -> None:
        if not self.available or self._window is None:
            return
        try:
            self._window.destroy()
        except AttributeError:
            pass
        self.available = False
