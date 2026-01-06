"""HUD elements for the game."""

from __future__ import annotations

import pygame


class Hud:
    def __init__(self, window_size: tuple[int, int]) -> None:
        self.window_size = window_size
        self.score_font = pygame.font.SysFont("arial", 28, bold=True)

    def render_score(self, surface: pygame.Surface, score_left: int, score_right: int) -> None:
        score_text = f"{score_left}   :   {score_right}"
        score_surf = self.score_font.render(score_text, True, (235, 240, 245))
        score_rect = score_surf.get_rect(center=(self.window_size[0] // 2, 36))
        surface.blit(score_surf, score_rect)
