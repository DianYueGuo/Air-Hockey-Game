"""Audio loading and playback."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOUND_DIR = PROJECT_ROOT / "assets" / "sounds" / "default"


@dataclass
class SoundPack:
    puck_hit_wall: Optional[pygame.mixer.Sound]
    puck_hit_mallet: Optional[pygame.mixer.Sound]
    goal: Optional[pygame.mixer.Sound]
    puck_move: Optional[pygame.mixer.Sound]


class AudioManager:
    def __init__(self, sound_dir: Path | None = None) -> None:
        self.enabled = True
        self.sound_dir = sound_dir or DEFAULT_SOUND_DIR
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            self.enabled = False
        self.sounds = self._load_sounds()

    def _load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        path = self.sound_dir / filename
        if not path.exists():
            return None
        try:
            return pygame.mixer.Sound(path.as_posix())
        except pygame.error:
            return None

    def _load_sounds(self) -> SoundPack:
        return SoundPack(
            puck_hit_wall=self._load_sound("puck_hit_wall.wav"),
            puck_hit_mallet=self._load_sound("puck_hit_mallet.wav"),
            goal=self._load_sound("goal.wav"),
            puck_move=self._load_sound("puck_move.wav"),
        )

    def play_wall(self) -> None:
        if self.enabled and self.sounds.puck_hit_wall:
            self.sounds.puck_hit_wall.play()

    def play_mallet(self) -> None:
        if self.enabled and self.sounds.puck_hit_mallet:
            self.sounds.puck_hit_mallet.play()

    def play_goal(self) -> None:
        if self.enabled and self.sounds.goal:
            self.sounds.goal.play()
