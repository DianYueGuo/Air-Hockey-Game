"""Entity specs for physics bodies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PuckSpec:
    radius: float = 0.04
    density: float = 0.8
    friction: float = 0.0
    restitution: float = 0.9
    linear_damping: float = 0.0


@dataclass(frozen=True)
class MalletSpec:
    radius: float = 0.07
    density: float = 5.0
    friction: float = 0.05
    restitution: float = 1.0
    linear_damping: float = 0.2
