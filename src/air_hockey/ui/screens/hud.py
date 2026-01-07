"""HUD elements for the game."""

from __future__ import annotations

import pygame

from air_hockey.ui.fonts import get_font


class Hud:
    def __init__(self, window_size: tuple[int, int], score_color: tuple[int, int, int]) -> None:
        self.window_size = window_size
        self.score_color = score_color
        self.score_font = get_font(28, bold=True)

    def render_score(self, surface: pygame.Surface, score_left: int, score_right: int) -> None:
        score_text = f"{score_left}   :   {score_right}"
        score_surf = self.score_font.render(score_text, True, self.score_color)
        score_rect = score_surf.get_rect(center=(self.window_size[0] // 2, 36))
        surface.blit(score_surf, score_rect)
