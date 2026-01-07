"""Playfield sizing and layout."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    width: float = 2.0
    height: float = 1.0
    wall_thickness: float = 0.05
    goal_height: float = 0.35
