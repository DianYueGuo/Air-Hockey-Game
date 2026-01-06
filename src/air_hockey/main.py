"""Main entry point for the Air Hockey game."""

import sys


def main() -> int:
    try:
        import pygame
    except ImportError as exc:
        print("pygame is required to run the game. Install dependencies first.")
        print(str(exc))
        return 1

    pygame.init()
    window_size = (960, 540)
    screen = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Air Hockey")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((15, 20, 30))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
