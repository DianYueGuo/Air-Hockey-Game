"""Font helpers with graceful fallback when pygame fonts are unavailable."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import pygame

FontKind = Literal["pygame", "freetype", "fallback"]

_BITMAP_FONT = {
    "A": ["0110", "1001", "1001", "1111", "1001", "1001", "1001"],
    "B": ["1110", "1001", "1001", "1110", "1001", "1001", "1110"],
    "C": ["0111", "1000", "1000", "1000", "1000", "1000", "0111"],
    "D": ["1110", "1001", "1001", "1001", "1001", "1001", "1110"],
    "E": ["1111", "1000", "1000", "1110", "1000", "1000", "1111"],
    "F": ["1111", "1000", "1000", "1110", "1000", "1000", "1000"],
    "G": ["0111", "1000", "1000", "1011", "1001", "1001", "0111"],
    "H": ["1001", "1001", "1001", "1111", "1001", "1001", "1001"],
    "I": ["111", "010", "010", "010", "010", "010", "111"],
    "J": ["0011", "0001", "0001", "0001", "0001", "1001", "0110"],
    "K": ["1001", "1010", "1100", "1000", "1100", "1010", "1001"],
    "L": ["1000", "1000", "1000", "1000", "1000", "1000", "1111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["1001", "1101", "1011", "1001", "1001", "1001", "1001"],
    "O": ["0110", "1001", "1001", "1001", "1001", "1001", "0110"],
    "P": ["1110", "1001", "1001", "1110", "1000", "1000", "1000"],
    "Q": ["0110", "1001", "1001", "1001", "1011", "1001", "0111"],
    "R": ["1110", "1001", "1001", "1110", "1100", "1010", "1001"],
    "S": ["0111", "1000", "1000", "0110", "0001", "0001", "1110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["1001", "1001", "1001", "1001", "1001", "1001", "0110"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "W": ["10001", "10001", "10101", "10101", "10101", "11011", "10001"],
    "X": ["1001", "1001", "0110", "0100", "0110", "1001", "1001"],
    "Y": ["1001", "1001", "0110", "0100", "0100", "0100", "0100"],
    "Z": ["1111", "0001", "0010", "0100", "1000", "1000", "1111"],
    "0": ["0110", "1001", "1001", "1001", "1001", "1001", "0110"],
    "1": ["010", "110", "010", "010", "010", "010", "111"],
    "2": ["1110", "0001", "0001", "0110", "1000", "1000", "1111"],
    "3": ["1110", "0001", "0001", "0110", "0001", "0001", "1110"],
    "4": ["1001", "1001", "1001", "1111", "0001", "0001", "0001"],
    "5": ["1111", "1000", "1000", "1110", "0001", "0001", "1110"],
    "6": ["0111", "1000", "1000", "1110", "1001", "1001", "0110"],
    "7": ["1111", "0001", "0010", "0100", "0100", "0100", "0100"],
    "8": ["0110", "1001", "1001", "0110", "1001", "1001", "0110"],
    "9": ["0110", "1001", "1001", "0111", "0001", "0001", "1110"],
    ":": ["0", "1", "0", "0", "1", "0", "0"],
    ".": ["0", "0", "0", "0", "0", "1", "0"],
    "-": ["0", "0", "0", "111", "0", "0", "0"],
    "/": ["0001", "0010", "0010", "0100", "0100", "1000", "1000"],
    " ": ["0", "0", "0", "0", "0", "0", "0"],
}


@dataclass
class FontWrapper:
    font: Optional[object]
    kind: FontKind
    size: int

    def render(self, text: str, antialias: bool, color: tuple[int, int, int]) -> pygame.Surface:
        if self.kind == "pygame" and self.font:
            return self.font.render(text, antialias, color)
        if self.kind == "freetype" and self.font:
            surface, _ = self.font.render(text, fgcolor=color)
            return surface
        return render_bitmap_text(text, self.size, color)


def render_bitmap_text(text: str, size: int, color: tuple[int, int, int]) -> pygame.Surface:
    scale = max(1, size // 8)
    text = text.upper()
    glyphs = [
        _BITMAP_FONT.get(ch, _BITMAP_FONT[" "]) for ch in text
    ]
    widths = [len(row[0]) if row else 1 for row in glyphs]
    height = 7 * scale
    width = sum(w * scale for w in widths) + max(0, (len(glyphs) - 1) * scale)
    surface = pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
    x_offset = 0
    for glyph, glyph_width in zip(glyphs, widths):
        for y, row in enumerate(glyph):
            for x, bit in enumerate(row):
                if bit == "1":
                    rect = pygame.Rect(
                        x_offset + x * scale,
                        y * scale,
                        scale,
                        scale,
                    )
                    surface.fill(color, rect)
        x_offset += glyph_width * scale + scale
    return surface


def get_font(size: int, bold: bool = False) -> FontWrapper:
    try:
        import pygame.freetype as freetype

        freetype.init()
        font = freetype.SysFont("arial", size, bold=bold)
        return FontWrapper(font=font, kind="freetype", size=size)
    except Exception:
        pass

    try:
        pygame.font.init()
        font = pygame.font.SysFont("arial", size, bold=bold)
        return FontWrapper(font=font, kind="pygame", size=size)
    except Exception:
        return FontWrapper(font=None, kind="fallback", size=size)
