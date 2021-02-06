import random
from time import time
from pathlib import Path

import pygame
import pygame.freetype
from pygame.math import Vector2

from models import Item, Player, Enemy, Score, PauseBanner, PlayerKilledBanner
from constants import (
    FACING_WEST,
    BACKGROUND_SOUND,
    BOTTLE_PICKED_SFX,
    PLAYER_KILLED_SFX,
    ENDING_SOUND,

)
from transformations import greyscale
import settings


class Scene:
    def play(self):
        pass


class Game(Scene):
    def __init__(self, screen, display_size, main_clock):
        self.screen = screen
        self.display_size = display_size
        self.main_clock = main_clock
        # Pause settings
        self.paused = False
        self.last_paused = time()
        self.paused_surface = None
        self.paused_banner = PauseBanner(self.screen)
        # Killed State
        self.player_killed_banner = PlayerKilledBanner(self.screen)
        # Images
        self.sprites_image = pygame.image.load(Path("assets/sprites/sprites.png")).convert_alpha()
        self.background = self._create_background()
        # Sounds
        self.bottle_picked = pygame.mixer.Sound(Path(BOTTLE_PICKED_SFX))
        self.player_killed_sound = pygame.mixer.Sound(Path(PLAYER_KILLED_SFX))
        self.background_sound = pygame.mixer.Sound(BACKGROUND_SOUND)
        self.background_sound.set_volume(settings.VOLUME)
        self.ending_sound = pygame.mixer.Sound(Path(ENDING_SOUND))
        self.ending_sound.set_volume(settings.VOLUME)

        # Sprites
        self.score = Score(self.screen)
        # Player
        self.player = Player(self.screen, self.sprites_image, initial_position=(50, 50))
        self.player.velocity = Vector2(0, 0)

        # Enemy
        self.enemy = Enemy(self.screen, self.sprites_image,
                      skin='BLOOD_CRYING_MOB', facing=FACING_WEST,
                      initial_position=(self.screen.get_width(), 0))
        self.enemy.velocity = Vector2(-.5, .5)

        # Items
        self.mana = Item(self.screen, self.sprites_image)

    def _draw_background(self):
        self.screen.blit(self.background, (0, 0, *self.display_size))

    def _create_background(self) -> pygame.Surface:
        return pygame.transform.scale(
            self.sprites_image.subsurface(pygame.rect.Rect(0, 91, 64, 48)),
            (self.screen.get_rect().width, self.screen.get_rect().height)
        )

    def _update_display(self):
        self.all_sprites.clear(self.screen, self.background)
        self.all_sprites.update(player_position=self.player.center_position)
        sprites_dirty = self.all_sprites.draw(self.screen)

        pygame.display.update(sprites_dirty)

    def _pause(self):
        if time() - self.last_paused > 0.5:
            self.paused = not self.paused
            self.last_paused = time()
            if self.paused:
                self.player_killed_banner.kill()
                self._update_display()
                self.paused_surface = greyscale(pygame.display.get_surface())
                self.paused_surface.blit(*self.paused_banner.render())
                pygame.mixer.pause()
            else:
                if not self.player.alive():
                    self.all_sprites.add(self.player_killed_banner)
                self._draw_background()
                self._update_display()
                pygame.display.flip()
                pygame.mixer.unpause()

    def _restart(self):
        self._stop()
        return self._start()

    def _start(self):
        self._draw_background()
        pygame.display.flip()
        self.score.value = 0
        self.player.restore_initial_position()
        self.enemy.restore_initial_position()
        self.background_sound.play(loops=-1)
        self.player_sprites = pygame.sprite.RenderUpdates(self.player)
        self.item_sprites = pygame.sprite.RenderUpdates(self.mana)
        self.mobs_sprites = pygame.sprite.RenderUpdates(self.enemy)
        self.all_sprites = pygame.sprite.OrderedUpdates(
            self.score,
            self.mana,
            self.enemy,
            self.player,
        )
        self.paused = False

    def _stop(self):
        self.background_sound.stop()
        self.ending_sound.stop()

    def play(self):
        run = True
        self._start()

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
                        self._stop()
                    elif event.key == pygame.K_r:
                        self._restart()
                    elif event.key in (pygame.K_p, pygame.K_PAUSE):
                        self._pause()
                    elif not self.paused:
                        self.player.on_key_pressed(event.key, pygame.key.get_pressed())

            if not self.paused:
                # COLISSIONS ++++++++
                if self.player.alive() and pygame.sprite.spritecollide(self.player, self.mobs_sprites, dokill=False):
                    self.player.kill()
                    self.all_sprites.add(self.player_killed_banner)
                    self.player_killed_sound.play()
                    self.background_sound.stop()
                    self.ending_sound.play(loops=-1)
                    self.enemy.velocity.update(0, 0)
                    self.enemy.acceleration.update(0.01, 0.01)

                if pygame.sprite.spritecollide(self.player, self.item_sprites,
                                               dokill=False,
                                               collided=pygame.sprite.collide_rect_ratio(0.7)):
                    self.score.value += 1
                    self.bottle_picked.play()
                    self.mana.spawn()
                # +++++++++++++++++++
                self._update_display()
            else:
                self.screen.blit(self.paused_surface, (0, 0, *self.display_size))
                pygame.display.update()
            self.main_clock.tick(60)


class TextScene(Scene):
    def __init__(self, screen, display_size, main_clock, background, path):
        self.screen = screen
        self.display_size = display_size
        self.main_clock = main_clock
        self.fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 20)
        self.fnt.pad = True
        self.credits_text = Path(path)
        self.background = background

    def align(self, line_rect, last_y):
        line_rect.y += last_y
        line_rect.centerx = self.screen.get_width() / 2
        return line_rect

    def play(self):
        self.screen.blit(self.background, (0, 0, *self.display_size))
        last_y = 50
        with self.credits_text.open(mode="r") as credits_file:
            lines = credits_file.readlines()
            for line in lines:
                line = line.strip("\n")
                line_surface, _ = self.fnt.render(line, fgcolor=pygame.color.Color('white'))
                line_rect = self.align(line_surface.get_rect(), last_y)
                last_y += line_rect.height
                self.screen.blit(line_surface, line_rect)
        pygame.display.flip()

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        run = False
            self.main_clock.tick(10)


class CreditsScene(TextScene):
    def __init__(self, *args, **kwargs):
        super().__init__(path=Path("./assets/text/credits.txt"), *args, **kwargs)


class ControlsScene(TextScene):
    def __init__(self, *args, **kwargs):
        super().__init__(path=Path("./assets/text/controls.txt"), *args, **kwargs)

    def align(self, line_rect, last_y):
        line_rect.y += last_y
        line_rect.x = self.screen.get_width() / 4
        return line_rect
