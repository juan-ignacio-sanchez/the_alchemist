import time
import random
from pathlib import Path

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.math import Vector2

import settings
from constants import (
    FACING_WEST,
    FACING_EAST,
    CHARACTERS_DICT,
    MOBS_DICT,
    WIDE_GREEN_LIQUID_ITEM,
    WIDE_BLUE_LIQUID_ITEM,
    WIDE_RED_LIQUID_ITEM,
    WALL_HIT_SFX,
    MENU_ITEM_CHANGED_SFX,
    BASIC_SWORD,
    SCALE_FACTOR,
    ITEMS_SCALE_FACTOR,
)


class Item(Sprite):
    RED = 0
    GREEN = 1
    BLUE = 2
    BOTTLE_COLORS = {
        RED: WIDE_RED_LIQUID_ITEM,
        BLUE: WIDE_BLUE_LIQUID_ITEM,
        GREEN: WIDE_GREEN_LIQUID_ITEM,
    }

    def __init__(self, surface, image, initial_position=(100, 100)):
        super().__init__()
        self.surface = surface
        self.original_image = image
        self.spawn()
        self.rect.center = initial_position

    def spawn(self, position=None, color=None):
        if not color:
            self.color = random.choice(range(len(Item.BOTTLE_COLORS)))
        else:
            self.color = color
        skin_rect = pygame.Rect(Item.BOTTLE_COLORS[self.color])
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * ITEMS_SCALE_FACTOR for side in skin_rect.size])
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(
            random.randint(100, self.surface.get_width() - 100),
            random.randint(100, self.surface.get_height() - 100)
        )


class Walker(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, skin='OLD_MAN', facing=FACING_EAST,
                 initial_position=(50, 50)):
        super().__init__()
        self.surface = surface

        # Skin related stuff
        self.skin = skin
        self.original_image = image
        self.set_skin()
        self.last_skin_change = time.time()
        self.facing = facing

        self.initial_position = initial_position
        self.rect = self.image.get_rect()
        self.rect.center = initial_position

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Sound
        self.knock = pygame.mixer.Sound(Path(WALL_HIT_SFX))
        self.knock.set_volume(settings.SFX_VOLUME)

    def restore_initial_position(self):
        self.velocity.update(0, 0)
        self.acceleration.update(0, 0)
        self.center_position.update(self.initial_position)
        self.rect.center = self.center_position

    def set_skin(self):
        pass

    def apply_force(self, force: Vector2):
        self.acceleration += force

    def apply_gravity(self):
        self.apply_force(Vector2(0, .002))

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration.update(0, 0)

    def bounce(self):
        FRICTION = 0.2
        vel_copy = Vector2(self.velocity)
        if not 0 < self.center_position.x:
            self.center_position.x = 0
            self.velocity.x *= -1 * FRICTION
            self.knock.play()
        elif not self.center_position.x < self.surface.get_width():
            self.center_position.x = self.surface.get_width()
            self.velocity.x *= -1 * FRICTION
            self.knock.play()

        if not 70 < self.center_position.y:
            self.center_position.y = 70
            self.velocity.y *= -1 * FRICTION
            self.knock.play()
        elif not self.center_position.y < self.surface.get_height() - 20:
            self.center_position.y = self.surface.get_height() - 20
            self.velocity.y *= -1 * FRICTION
            self.knock.play()


class Enemy(Walker):
    def change_facing(self):
        if self.velocity.x > 0 and not self.facing == FACING_EAST:
            self.facing = FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.velocity.x < 0 and not self.facing == FACING_WEST:
            self.facing = FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, *args, **kwargs) -> None:
        # Follow the player
        distance_vector = (kwargs.get('player_position') - self.center_position).normalize()
        self.apply_force(distance_vector * 2 / self.rect.height)
        self.move()
        self.bounce()
        self.change_facing()

    def set_skin(self):
        self.facing = FACING_WEST
        skin_rect = pygame.rect.Rect(MOBS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * SCALE_FACTOR for side in skin_rect.size])


class Player(Walker):
    def set_skin(self):
        skin_rect = pygame.rect.Rect(CHARACTERS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * SCALE_FACTOR for side in skin_rect.size])

    def change_facing(self, key):
        if key == pygame.K_RIGHT and not self.facing == FACING_EAST:
            self.facing = FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif key == pygame.K_LEFT and not self.facing == FACING_WEST:
            self.facing = FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def on_key_pressed(self, event_key, keys):
        magnitude = .5
        if keys[pygame.K_RIGHT]:
            self.apply_force(Vector2(magnitude, 0))
        if keys[pygame.K_LEFT]:
            self.apply_force(Vector2(-magnitude, 0))
        if keys[pygame.K_UP]:
            self.apply_force(Vector2(0, -magnitude))
        if keys[pygame.K_DOWN]:
            self.apply_force(Vector2(0, magnitude))

        self.change_facing(event_key)

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()


class Weapon(Sprite):
    STATIC = 0
    UP = 1
    DOWN = 2

    def __init__(self, surface, image, owner: Player):
        super().__init__()
        self.surface = surface
        self.original_image = image
        self.owner = owner
        self.sound = pygame.mixer.Sound(Path("assets/sounds/sfx/sword_brandishing.wav"))
        self.sound.set_volume(settings.SFX_VOLUME)

        weapon_rect = pygame.Rect(BASIC_SWORD)
        self.image = self.original_image.subsurface(weapon_rect)
        self.image = pygame.transform.scale(self.image, [side * ITEMS_SCALE_FACTOR for side in weapon_rect.size])
        self._image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center

        self.brandishing = Weapon.STATIC
        self.pivot = Vector2(self.rect.centerx, self.rect.centery + (self.rect.height // 2))
        self.rotation_vector = self.rect.center - self.pivot
        self.sword_angle = 0
        self.angle_diff = 0.5

    def update(self, *args, **kwargs):
        FACING = 1 if self.owner.facing == FACING_EAST else -1
        if self.brandishing == Weapon.DOWN:
            self.sword_angle += self.angle_diff
            if self.sword_angle >= 170:
                self.brandishing = Weapon.UP
        elif self.brandishing == Weapon.UP and self.sword_angle > 0:
            self.sword_angle -= self.angle_diff
        else:
            self.angle_diff = 1
            self.sword_angle = 0
            self.brandishing = Weapon.STATIC

        self.angle_diff += 9
        self.image = pygame.transform.rotate(self._image, -FACING * self.sword_angle)
        rotated_vector = self.rotation_vector.rotate(FACING * self.sword_angle)
        relocation_vector = rotated_vector - self.rotation_vector
        self.rect = self.image.get_rect()
        self.rect.center = self.owner.rect.center
        self.rect.centerx += FACING * (self.owner.rect.width / 1.5)
        self.rect.centery -= self.owner.rect.height / 4
        self.rect.center += relocation_vector
        if not self.owner.alive():
            self.kill()

    def on_key_pressed(self, event_key, keys):
        if keys[pygame.K_SPACE] and self.brandishing == Weapon.STATIC:
            self.brandishing = Weapon.DOWN
            self.sound.play()
