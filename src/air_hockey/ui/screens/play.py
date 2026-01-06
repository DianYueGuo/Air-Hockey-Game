"""Playable field with Box2D physics (no controls yet)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import pygame

from air_hockey.engine.physics import PhysicsWorld
from air_hockey.game.field import FieldSpec


@dataclass
class RenderConfig:
    pixels_per_meter: float
    table_rect: pygame.Rect


class PlayScreen:
    def __init__(self, window_size: tuple[int, int], on_back: Callable[[], None]) -> None:
        self.window_size = window_size
        self.on_back = on_back
        self.field = FieldSpec()
        self.physics = PhysicsWorld(self.field)
        self.clock_accumulator = 0.0
        self.fixed_time_step = 1.0 / 120.0
        self.render_config = self._build_render_config()
        self.font = pygame.font.SysFont("arial", 22)

    def _build_render_config(self) -> RenderConfig:
        table_width_px = int(self.field.width * 400)
        table_height_px = int(self.field.height * 400)
        table_rect = pygame.Rect(0, 0, table_width_px, table_height_px)
        table_rect.center = (self.window_size[0] // 2, self.window_size[1] // 2)
        return RenderConfig(pixels_per_meter=400.0, table_rect=table_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_back()

    def update(self, dt: float) -> None:
        self.clock_accumulator += dt
        while self.clock_accumulator >= self.fixed_time_step:
            self.physics.step(self.fixed_time_step)
            self.clock_accumulator -= self.fixed_time_step

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((10, 16, 22))
        self._draw_table(surface)
        self._draw_entities(surface)
        hint = self.font.render("ESC to return to menu", True, (180, 190, 205))
        surface.blit(hint, (16, 16))

    def _world_to_screen(self, position: tuple[float, float]) -> tuple[int, int]:
        px = position[0] * self.render_config.pixels_per_meter
        py = position[1] * self.render_config.pixels_per_meter
        center_x, center_y = self.render_config.table_rect.center
        return int(center_x + px), int(center_y + py)

    def _draw_table(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (32, 44, 58), self.render_config.table_rect, border_radius=16)
        pygame.draw.rect(surface, (90, 110, 130), self.render_config.table_rect, width=4, border_radius=16)
        center_x = self.render_config.table_rect.centerx
        pygame.draw.line(
            surface,
            (70, 90, 110),
            (center_x, self.render_config.table_rect.top),
            (center_x, self.render_config.table_rect.bottom),
            width=2,
        )

    def _draw_entities(self, surface: pygame.Surface) -> None:
        puck = self.physics.entities.puck
        mallet_left = self.physics.entities.mallet_left
        mallet_right = self.physics.entities.mallet_right

        self._draw_circle(surface, puck.position, 0.04, (220, 230, 240))
        self._draw_circle(surface, mallet_left.position, 0.07, (70, 170, 230))
        self._draw_circle(surface, mallet_right.position, 0.07, (230, 90, 90))

    def _draw_circle(
        self, surface: pygame.Surface, position: tuple[float, float], radius: float, color: tuple[int, int, int]
    ) -> None:
        screen_pos = self._world_to_screen(position)
        radius_px = int(radius * self.render_config.pixels_per_meter)
        pygame.draw.circle(surface, color, screen_pos, radius_px)
        pygame.draw.circle(surface, (20, 30, 40), screen_pos, radius_px, width=2)
