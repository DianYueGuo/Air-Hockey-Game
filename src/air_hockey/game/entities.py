"""Entity specs for physics bodies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PuckSpec:
    radius: float = 0.04
    density: float = 0.8
    friction: float = 0.1
    restitution: float = 0.9
    linear_damping: float = 0.05


@dataclass(frozen=True)
class MalletSpec:
    radius: float = 0.07
    density: float = 1.6
    friction: float = 0.2
    restitution: float = 0.9
    linear_damping: float = 1.5
