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
    from air_hockey.app import App

    app = App(window_size=(960, 540))
    exit_code = app.run()
    pygame.quit()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
