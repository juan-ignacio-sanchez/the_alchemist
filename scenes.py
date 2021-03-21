from time import time
from pathlib import Path
from random import choice

import pygame
import pygame.freetype
from pygame.math import Vector2

from sprites.models import (
    Item,
    Walker,
    Player,
    Enemy,
    Weapon,
)
from sprites.ui import (
    Score,
    PauseBanner,
    PlayerKilledBanner,
    PlayerWonBanner
)
from sprites.images import load_sprites
from transformations import greyscale, blur
import constants
import settings


class Scene:
    def play(self):
        pass


class Level:
    def __init__(self, screen, display_size, max_score,
                 allowed_enemies=None, allowed_potions=None):
        self.screen = screen
        self.score = Score(self.screen, max_score=max_score, seconds_to_leave=5)
        self.allowed_enemies = allowed_enemies or [
            constants.MOB_BIG_TROLL,
        ]
        self.allowed_potions = allowed_potions or [
            constants.POTION_GREEN,
            constants.POTION_RED,
            constants.POTION_BLUE,
        ]

    def random_enemy(self):
        return choice(self.allowed_enemies)

    def random_potion(self):
        return choice(self.allowed_potions)


class Game(Scene):
    def __init__(self, screen, display_size, main_clock):
        self.screen = screen
        self.display_size = display_size
        self.main_clock = main_clock
        self.run = True
        # Pause settings
        self.paused = False
        self.last_paused = time()
        self.paused_surface = None
        self.paused_banner = PauseBanner(self.screen)
        # Restart settings
        self.last_restarted = time()
        # Killed State
        self.player_killed_banner = PlayerKilledBanner(self.screen)
        # Won State
        self.player_won_banner = PlayerWonBanner(self.screen)
        # Images
        self.sprites_image = load_sprites()
        self.background = self._create_background()
        # Sounds
        self.bottle_picked = pygame.mixer.Sound(Path(constants.BOTTLE_PICKED_SFX))
        self.bottle_picked.set_volume(settings.SFX_VOLUME)
        self.player_killed_sound = pygame.mixer.Sound(Path(constants.PLAYER_KILLED_SFX))
        self.player_killed_sound.set_volume(settings.SFX_VOLUME)
        self.background_sound = pygame.mixer.Sound(constants.BACKGROUND_SOUND)
        self.background_sound.set_volume(settings.VOLUME)
        self.ending_sound = pygame.mixer.Sound(Path(constants.ENDING_SOUND))
        self.ending_sound.set_volume(settings.VOLUME)
        self.player_won_sound = pygame.mixer.Sound(Path(constants.PLAYER_WIN_SFX))
        self.player_won_sound.set_volume(settings.SFX_VOLUME)

        # Level Configuration
        self.current_level = Level(screen, screen.get_size(), max_score=5)

        # Sprites
        self.potions_sprites = pygame.sprite.RenderUpdates()
        self.mobs_sprites = pygame.sprite.RenderUpdates()
        self.player_sprites = pygame.sprite.RenderUpdates()
        self.all_sprites = pygame.sprite.LayeredUpdates()

    def _draw_background(self):
        self.screen.blit(self.background, (0, 0, *self.display_size))

    def _create_background(self) -> pygame.Surface:
        floor_surface = pygame.transform.scale(
            self.sprites_image.subsurface(pygame.rect.Rect(constants.FLOOR_BACKGROUND)),
            (self.screen.get_rect().width, self.screen.get_rect().height)
        )
        steps = constants.SCALE_FACTOR
        walls = []
        original_wall_up_height = self.sprites_image.subsurface(constants.WALL_BACKGROUND).get_rect().height
        new_wall_up_height = self.screen.get_rect().height // constants.SCALE_FACTOR
        original_wall_down_height = self.sprites_image.subsurface(constants.WALL_FRONT_BACKGROUND).get_rect().height
        new_wall_down_height = (original_wall_down_height * new_wall_up_height) // original_wall_up_height
        for i in range(steps):
            wall_surface_up = pygame.transform.scale(
                self.sprites_image.subsurface(constants.WALL_BACKGROUND),
                (self.screen.get_rect().width // steps, new_wall_up_height)
            )
            rect = wall_surface_up.get_rect()
            rect.x += i * rect.width
            walls.append((wall_surface_up, rect))

            wall_surface_down = pygame.transform.scale(
                self.sprites_image.subsurface(constants.WALL_FRONT_BACKGROUND),
                (self.screen.get_rect().width // steps, new_wall_down_height)
            )
            rect = wall_surface_up.get_rect()
            rect.x += i * rect.width
            rect.y = self.screen.get_rect().height - new_wall_down_height
            walls.append((wall_surface_down, rect))

        floor_surface.blits(walls)

        # Draw columns
        column_surface = self.sprites_image.subsurface(constants.BACKGROUND_COLUMN)
        column_surface = pygame.transform.scale(column_surface, [x * constants.SCALE_FACTOR for x in column_surface.get_size()])
        floor_surface.blits((
            (column_surface, (0, 0)),
            (column_surface, (self.screen.get_rect().centerx - column_surface.get_rect().centerx, 0)),
            (column_surface, (self.screen.get_rect().right - column_surface.get_width(), 0)),
        ))

        return floor_surface

    def _update_display(self):
        self.all_sprites.clear(self.screen, self.background)
        self.all_sprites.update(player_position=self.player.center_position)
        sprites_dirty = self.all_sprites.draw(self.screen)
        pygame.display.update(sprites_dirty)

    def _spawn_score(self):
        self.current_level.score.value = 0
        self.all_sprites.add(
            self.current_level.score,
        )

    def _spawn_player(self):
        player = Player(
            self.screen,
            initial_position=(
                70, self.screen.get_rect().height - 70
            )
        )
        self.player_sprites.add(player)
        self.all_sprites.add(player)
        return player

    def _spawn_potion(self):
        potion = Item(self.screen, self.sprites_image, self.current_level.random_potion())
        self.potions_sprites.add(potion)
        self.all_sprites.add(potion)
        return potion

    def _spawn_enemy(self, initial_position=None, enemy=None):
        enemy = Enemy(
            self.screen,
            particles_group=self.all_sprites,
            skin=self.current_level.random_enemy(),
            facing=constants.FACING_WEST,  # TODO: this doesn't looks quite right.
            initial_position=initial_position or (self.screen.get_width(), 60)
        )
        self.mobs_sprites.add(enemy)
        self.all_sprites.add(enemy)
        return enemy

    def _spawn_weapon(self, owner: Player):
        # Weapons
        weapon = Weapon(self.screen, self.sprites_image, owner)
        return weapon

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
        if time() - self.last_restarted > 0.5:
            self._stop(instantly=True)
            self._start()
        self.last_restarted = time()

    def _start(self):
        self.player_sprites.empty()
        self.mobs_sprites.empty()
        self.potions_sprites.empty()
        self.all_sprites.empty()
        self._spawn_potion()
        self._spawn_enemy()
        self._spawn_score()
        self.player = self._spawn_player()
        self.weapon = self._spawn_weapon(owner=self.player)

        self.run = True
        self.paused = False
        self._draw_background()
        pygame.display.flip()
        self.background_sound.play(loops=-1)

    def _stop(self, instantly=False):
        self.run = False
        fadeout = self.current_level.score.transition_seconds * 1000 if not instantly else 0
        self.background_sound.fadeout(fadeout)
        self.ending_sound.fadeout(fadeout)

    def play(self):
        self._start()

        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._stop()
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._stop()
                    elif event.key == pygame.K_r:
                        self._restart()
                    elif event.key in (pygame.K_p, pygame.K_PAUSE):
                        self._pause()
                    elif not self.paused:
                        self.player.on_key_pressed(event.key, pygame.key.get_pressed())
                        self.weapon.on_key_pressed(event.key, pygame.key.get_pressed())

            # I want this collision to always be computed.
            if pygame.sprite.collide_rect(self.player, self.current_level.score):
                self.current_level.score.hide()
            else:
                self.current_level.score.show()

            if self.current_level.score.won():
                if not self.all_sprites.has(self.player_won_banner):
                    self.all_sprites.add(self.player_won_banner)
                if self.current_level.score.quit_transition():
                    self.screen.blit(blur(pygame.display.get_surface(), 2), (0, 0, *self.display_size))
                    pygame.display.flip()
                elif self.current_level.score.is_time_to_leave():
                    self._update_display()
                    self._stop()
                else:
                    self._update_display()
            elif self.paused:
                self.screen.blit(self.paused_surface, (0, 0, *self.display_size))
                pygame.display.update()
            else:
                # COLLISIONS ++++++++
                if self.player.alive():
                    player_mobs_collide = pygame.sprite.spritecollide(self.player, self.mobs_sprites, dokill=False)
                    if player_mobs_collide:
                        self.player.kill()
                        self.all_sprites.add(self.player_killed_banner)
                        self.player_killed_sound.play()
                        self.background_sound.stop()
                        self.ending_sound.play(loops=-1)
                        enemy: Enemy
                        for enemy in self.mobs_sprites:
                            enemy.velocity.update(0, 0)
                            enemy.acceleration.update(0.01, 0.01)
                    elif self.weapon.alive() and self.weapon.brandishing != Weapon.STATIC:
                        weapon_mobs_collide = pygame.sprite.spritecollide(self.weapon, self.mobs_sprites, dokill=False)
                        enemy: Enemy
                        for enemy in weapon_mobs_collide:
                            particles = enemy.hurt(self.player.center_position)
                            if particles:
                                self.all_sprites.add(particles)
                        # self.weapon.kill()

                    bottles_picked = pygame.sprite.spritecollide(
                        self.player, self.potions_sprites,
                        dokill=False, collided=pygame.sprite.collide_rect_ratio(0.7))

                    if bottles_picked:
                        self.bottle_picked.play()
                        self.current_level.score.increase()
                        bottle: Item
                        for bottle in bottles_picked:
                            if bottle.color == Item.RED:
                                self._spawn_enemy(
                                    initial_position=(
                                        self.player.center_position
                                        + self.player.velocity * -70
                                    )
                                )
                            elif bottle.color == Item.BLUE:
                                self.all_sprites.add(self.weapon)
                            if not self.current_level.score.won():
                                bottle.spawn()
                            else:
                                bottle.kill()
                        if self.current_level.score.won():
                            self.background_sound.fadeout(2000)
                            self.player_won_sound.play(0, 0, 500)
                            enemy: Enemy
                            for enemy in self.mobs_sprites:
                                enemy.die(self.player.center_position)
                    # +++++++++++++++++++
                self._update_display()
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
