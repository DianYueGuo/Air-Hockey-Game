"""Reusable UI widgets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame


@dataclass
class Button:
    rect: pygame.Rect
    label: str
    on_click: Callable[[], None]
    font: pygame.font.Font

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        mouse_pos = pygame.mouse.get_pos()
        is_hover = self.rect.collidepoint(mouse_pos)
        bg_color = (70, 90, 120) if is_hover else (50, 60, 80)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (120, 140, 170), self.rect, width=2, border_radius=8)

        text_surf = self.font.render(self.label, True, (230, 235, 240))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
