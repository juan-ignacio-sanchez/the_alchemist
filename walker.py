import random
from collections import namedtuple
from pathlib import Path
from pygame.examples import aliens

from scenes import Game
from transformations import blur, greyscale

import pygame

Size = namedtuple('Size', ['width', 'height'])


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    pygame.key.set_repeat(1, 32)
    main_clock = pygame.time.Clock()
    display_size = Size(width=800, height=600)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE, vsync=1)

    # Scenes (Main Menu, Credits, Game itself...)
    game = Game(screen, display_size, main_clock)

    # menu_background = blur(game.background.copy(), level=10)
    menu_background = greyscale(game.background.copy())
    main_menu_sound = pygame.mixer.Sound("assets/sounds/main_menu.mp3")
    main_menu_sound.set_volume(0.09)
    main_menu_sound.play(loops=-1)

    run = True
    close = False
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or close:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_RETURN:
                    close = game.play()
        screen.blit(menu_background, (0, 0, *screen.get_size()))
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
