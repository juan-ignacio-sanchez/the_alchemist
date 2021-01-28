import os
from collections import namedtuple

from scenes import Game
from models import MainMenu

import pygame
import pygame.freetype

Size = namedtuple('Size', ['width', 'height'])


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()
    main_clock = pygame.time.Clock()
    display_size = Size(width=800, height=600)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE, vsync=1)
    # Scenes (Main Menu, Credits, Game itself...)
    game = Game(screen, display_size, main_clock)

    menu_background = game.background
    main_menu_sound = pygame.mixer.Sound("assets/sounds/main_menu.mp3")
    main_menu_sound.set_volume(0.09)
    main_menu_sound.play(loops=-1)

    main_menu = MainMenu(screen)
    main_menu_sprites = pygame.sprite.RenderUpdates(main_menu)
    screen.blit(menu_background, (0, 0, *screen.get_size()))
    pygame.display.flip()

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
                    pygame.key.set_repeat(1, 32)
                    main_menu_sound.stop()
                    close = game.play()
                    main_menu_sound.set_volume(0.09)
                    main_menu_sound.play(loops=-1)
                elif event.key == pygame.K_x:
                    main_menu.next_option()

        main_menu_sprites.clear(screen, menu_background)
        main_menu_sprites.update()
        sprites_dirty = main_menu_sprites.draw(screen)

        pygame.display.update(sprites_dirty)

    pygame.quit()


if __name__ == '__main__':
    main()
