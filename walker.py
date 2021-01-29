from collections import namedtuple

import pygame
import pygame.freetype

import settings
from scenes import Game
from models import MainMenu
from transformations import greyscale

Size = namedtuple('Size', ['width', 'height'])


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()
    main_clock = pygame.time.Clock()
    display_size = Size(width=1280, height=800)
    screen = pygame.display.set_mode(display_size, settings.DISPLAY_MODE, vsync=1)
    # Scenes (Main Menu, Credits, Game itself...)
    game = Game(screen, display_size, main_clock)

    menu_background = greyscale(game.background)
    main_menu_sound = pygame.mixer.Sound("assets/sounds/main_menu.mp3")
    main_menu_sound.set_volume(settings.VOLUME)
    main_menu_sound.play(loops=-1)

    main_menu = MainMenu(screen)
    main_menu_sprites = pygame.sprite.RenderUpdates(main_menu)
    screen.blit(menu_background, (0, 0, *screen.get_size()))
    pygame.display.flip()

    run = True
    force_quit = False
    selected_option = main_menu.selected_option
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or force_quit:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    run = False
                elif event.key == pygame.K_RETURN:
                    if selected_option == MainMenu.options.START:
                        pygame.key.set_repeat(1, 32)
                        main_menu_sound.stop()
                        force_quit = game.play()
                        ### Restore main menu ###
                        screen.blit(menu_background, (0, 0, *screen.get_size()))
                        pygame.display.flip()
                        main_menu_sound.set_volume(settings.VOLUME)
                        main_menu_sound.play(loops=-1)
                        pygame.key.set_repeat()
                    elif selected_option == MainMenu.options.QUIT:
                        run = False
                elif event.key == pygame.K_UP:
                    selected_option = main_menu.prev_option()
                elif event.key == pygame.K_DOWN:
                    selected_option = main_menu.next_option()

        main_menu_sprites.clear(screen, menu_background)
        main_menu_sprites.update()
        sprites_dirty = main_menu_sprites.draw(screen)

        pygame.display.update(sprites_dirty)

    pygame.quit()


if __name__ == '__main__':
    main()
