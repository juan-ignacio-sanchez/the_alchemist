import random
from time import time
from pathlib import Path

import pygame
from pygame.math import Vector2

from models import Item, Player, Enemy, Score
from constants import FACING_WEST
from transformations import blur, greyscale


class Scene:
    pass


class Game(Scene):
    def __init__(self, screen, display_size, main_clock):
        self.screen = screen
        self.display_size = display_size
        self.main_clock = main_clock
        # Pause settings
        self.paused = False
        self.last_paused = time()
        self.blurred_surface = None
        # Images
        self.sprites_image = pygame.image.load("assets/sprites/sprites.png").convert()
        self.background = self._create_background()
        # Sounds
        self.bottle_picked = pygame.mixer.Sound("assets/sounds/bottle_picked.ogg")
        self.player_killed_sound = pygame.mixer.Sound("assets/sounds/kill.ogg")
        self.background_sound = pygame.mixer.Sound(self._select_background_sound())
        self.background_sound.set_volume(0.09)
        self.ending_sound = pygame.mixer.Sound("assets/sounds/ending.mp3")
        self.ending_sound.set_volume(0.09)

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

    def _select_background_sound(self):
        sounds = Path('assets/sounds/background/')
        return random.choice(list(sounds.glob("*.mp3")))

    def _create_background(self) -> pygame.Surface:
        return pygame.transform.scale(
            self.sprites_image.subsurface(pygame.rect.Rect(0, 91, 64, 48)),
            (self.screen.get_rect().width, self.screen.get_rect().height)
        )

    def _pause(self):
        if time() - self.last_paused > 0.5:
            self.paused = not self.paused
            self.last_paused = time()
            if self.paused:
                self.blurred_surface = greyscale(pygame.display.get_surface())
            else:
                self._draw_background()
                pygame.display.flip()

    def _restart(self):
        self._stop()
        return self._start()

    def _start(self):
        self._draw_background()
        pygame.display.flip()
        self.score.value = 0
        self.player.restore_initial_position()
        self.enemy.restore_initial_position()
        self.background_sound.play()
        self.player_sprites = pygame.sprite.RenderUpdates(self.player)
        self.item_sprites = pygame.sprite.RenderUpdates(self.mana)
        self.mobs_sprites = pygame.sprite.RenderUpdates(self.enemy)
        self.all_sprites = pygame.sprite.OrderedUpdates(
            self.score,
            self.mana,
            self.enemy,
            self.player,
        )

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
                        self.player.on_key_pressed(event.key)

            if not self.paused:
                # COLISSIONS ++++++++
                if self.player.alive() and pygame.sprite.spritecollide(self.player, self.mobs_sprites, dokill=False):
                    self.player.kill()
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

                self.all_sprites.clear(self.screen, self.background)
                self.all_sprites.update(player_position=self.player.center_position)
                sprites_dirty = self.all_sprites.draw(self.screen)

                pygame.display.update(sprites_dirty)
            else:
                self.screen.blit(self.blurred_surface, (0, 0, *self.display_size))
                pygame.display.update()
            self.main_clock.tick(60)
