import os
import sys
from collections import namedtuple
from pathlib import Path

import pygame
import pygame.freetype

import settings
from constants import MAIN_MENU_SOUND
from scenes import Game, CreditsScene, ControlsScene
from models import MainMenu
from transformations import greyscale

Size = namedtuple('Size', ['width', 'height'])


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.freetype.init()
    main_clock = pygame.time.Clock()
    monitor_info = pygame.display.Info()
    display_size = Size(width=monitor_info.current_w, height=monitor_info.current_h)

    if not sys.platform.startswith("linux"):
        if 0 != pygame.display.mode_ok(display_size, flags=settings.DISPLAY_MODE_FULL):
            screen = pygame.display.set_mode(display_size, settings.DISPLAY_MODE_FULL, vsync=1)
        else:
            screen = pygame.display.set_mode(display_size, settings.DISPLAY_MODE_WIND, vsync=1)
    else:
        # Unfortunately, for the moment I have to use windowed session on Linux because a bug in PyGame2
        screen = pygame.display.set_mode(display_size, settings.DISPLAY_MODE_WIND, vsync=0)

    # Scenes (Main Menu, Credits, Game itself...)
    game = Game(screen, display_size, main_clock)

    menu_background = greyscale(game.background)
    main_menu_sound = pygame.mixer.Sound(Path(MAIN_MENU_SOUND))
    main_menu_sound.set_volume(settings.VOLUME)
    main_menu_sound.play(loops=-1)

    main_menu = MainMenu(screen)
    main_menu_sprites = pygame.sprite.RenderUpdates(main_menu)

    credits_scene = CreditsScene(screen, display_size, main_clock, menu_background)
    controls_scene = ControlsScene(screen, display_size, main_clock, menu_background)

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
                    elif selected_option == MainMenu.options.CREDITS:
                        force_quit = credits_scene.play()
                        screen.blit(menu_background, (0, 0, *screen.get_size()))
                        pygame.display.flip()
                    elif selected_option == MainMenu.options.CONTROLS:
                        force_quit = controls_scene.play()
                        screen.blit(menu_background, (0, 0, *screen.get_size()))
                        pygame.display.flip()
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
        main_clock.tick(15)

    pygame.quit()


if __name__ == '__main__':
    if hasattr(sys, "_MEIPASS"):
        os.chdir(sys._MEIPASS)
    main()
