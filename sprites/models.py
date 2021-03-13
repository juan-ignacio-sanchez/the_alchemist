import time
import random
from pathlib import Path
from math import copysign
from typing import Tuple

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.math import Vector2

import settings
import constants
from transformations import greyscale, redscale


class Item(Sprite):
    RED = 0
    GREEN = 1
    BLUE = 2
    BOTTLE_COLORS = {
        RED: constants.WIDE_RED_LIQUID_ITEM,
        BLUE: constants.WIDE_BLUE_LIQUID_ITEM,
        GREEN: constants.WIDE_GREEN_LIQUID_ITEM,
    }

    def __init__(self, surface, image, initial_position=(100, 100)):
        super().__init__()
        self.layer = constants.LAYER_ITEM
        self.surface = surface
        self.original_image = image
        self.spawn()
        self.rect.center = initial_position

    def spawn(self, position=None, color=None):
        if color is None:
            self.color = random.choice(range(len(Item.BOTTLE_COLORS)))
        else:
            self.color = color
        skin_rect = pygame.Rect(Item.BOTTLE_COLORS[self.color])
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * constants.ITEMS_SCALE_FACTOR for side in skin_rect.size])
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(
            random.randint(100, self.surface.get_width() - 100),
            random.randint(100, self.surface.get_height() - 100)
        )


class Particle(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, initial_position: Tuple = (50, 50),
                 reference_force_vector: Vector2 = None):
        super().__init__()
        self.layer = constants.LAYER_PARTICLE
        self.surface = surface

        self.image = image

        self.initial_position = Vector2(initial_position)
        self.decay_distance = random.choice((*([random.randint(100, 200)] * 10), random.randint(250, 400)))
        self.rect = self.image.get_rect()
        self.rect.center = initial_position

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        angle = random.randint(-15000, 15000)
        magnitude = random.choice((*([random.randint(10, 100)] * 5), random.randint(100, 2500)))
        magnitude /= 200_000
        self.force_to_apply = reference_force_vector.rotate(angle / 1000) * magnitude

    def apply_force(self, force: Vector2):
        self.acceleration += force

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration.update(0, 0)

    def update(self, *args, **kwargs) -> None:
        self.apply_force(self.force_to_apply)
        self.move()
        if not self.surface.get_rect().contains(self.rect) or \
            self.initial_position.distance_to(self.center_position) > self.decay_distance:
            self.kill()

class Walker(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, skin='OLD_MAN', facing=constants.FACING_EAST,
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
        self._image = self.image.copy()

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Sound
        self.knock = pygame.mixer.Sound(Path(constants.WALL_HIT_SFX))
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

    def apply_friction(self):
        if self.velocity.magnitude():
            friction_force = self.velocity.normalize() * -0.1
            self.apply_force(friction_force)

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration.update(0, 0)

    def bounce(self):
        FRICTION = 0.2
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
    IMAGE_STATE_NORMAL = 0
    IMAGE_STATE_HURT = 1
    IMAGE_STATE_BACK_TO_NORMAL = 2
    IMAGE_STATE_DIE = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer = constants.LAYER_ENEMY
        self.banishing_sound = pygame.mixer.Sound(Path(constants.ENEMY_KILLED_SFX))
        self.banishing_sound.set_volume(settings.SFX_VOLUME)
        self.hearts = 3
        self.last_hit = time.time()
        self._back_to_normal = False
        # Change style of image
        self.image_state = self.IMAGE_STATE_NORMAL
        self._image = self.image.copy()
        self.restore_image = False
        self.last_player_position = Vector2(1, 0)
        self.rendering_group = None

    def change_facing(self):
        if self.velocity.x > 0 and not self.facing == constants.FACING_EAST:
            self.facing = constants.FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.velocity.x < 0 and not self.facing == constants.FACING_WEST:
            self.facing = constants.FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def limit_vector(self, vector, bottom, top):
        mag = vector.magnitude()
        if mag > top:
            force = vector.normalize() * top
        elif mag < bottom:
            force = vector.normalize() * bottom
        else:
            force = vector
        return force

    @staticmethod
    def different_quadrants(v: pygame.Vector2, w: pygame.Vector2) -> bool:
        return v.x != copysign(v.x, w.x) or v.y != copysign(v.y, w.y)

    def being_repeled(self):
        return (time.time_ns() - self.last_hit) <= 150_000_000

    def hurt(self, player_position: Vector2,
             rendering_group: pygame.sprite.AbstractGroup, hearts: int = 1):
        if not self.being_repeled():
            self.hearts -= 1
            self.apply_force(-self.velocity)
            self.apply_force((self.center_position - player_position).normalize() * 15)
            self.last_hit = time.time_ns()
            self.image = redscale(self.image)
            self.image_state = self.IMAGE_STATE_HURT
            self.last_player_position.update(player_position)
            self.rendering_group = rendering_group

    def update_image_state(self):
        if self.image_state == self.IMAGE_STATE_HURT and not self.being_repeled():
            self.image_state = self.IMAGE_STATE_BACK_TO_NORMAL
        if self.hearts <= 0 and not self.being_repeled():
            return self.die(self.last_player_position)

    def die(self, player_position: Vector2):
        PIECE_SIZE = 3
        self.kill()
        self.banishing_sound.play()
        # Slice squares the image apart.
        x_slices = self.rect.width // PIECE_SIZE
        y_slices = self.rect.height // PIECE_SIZE
        height = PIECE_SIZE
        width = PIECE_SIZE

        image = greyscale(self._image).convert_alpha()
        particles = []
        for slice_x_position in range(x_slices):
            vertical_offset = 0
            for slice in range(y_slices):
                subsurf = image.subsurface(slice_x_position * width, vertical_offset, width, height)
                x, y = subsurf.get_offset()
                particles.append(Particle(
                    surface=self.surface,
                    image=subsurf,
                    initial_position=(self.rect.x + x, self.rect.y + y),
                    reference_force_vector=self.center_position - player_position
                ))
                vertical_offset += height
        if self.rendering_group:
            self.rendering_group.add(particles)

    def update(self, *args, **kwargs) -> None:
        player_position = Vector2(kwargs.get('player_position'))
        # Follow the player
        distance_vector = Vector2(player_position - self.center_position)
        distance_vector.scale_to_length(distance_vector.magnitude())
        force = self.limit_vector(distance_vector, .005, 0.1)

        # Extra force if going in "opposite" directions
        if Enemy.different_quadrants(self.velocity, player_position):
            force *= 3

        self.update_image_state()
        if self.image_state == self.IMAGE_STATE_BACK_TO_NORMAL:
            self.image = self._image.copy()
            self.image_state = self.IMAGE_STATE_NORMAL

        self.apply_force(force)
        self.move()
        self.bounce()
        self.change_facing()

    def set_skin(self):
        self.facing = constants.FACING_WEST
        skin_rect = pygame.rect.Rect(constants.MOBS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * constants.SCALE_FACTOR for side in skin_rect.size])
        self.rect = self.image.get_rect()


class Player(Walker):
    def set_skin(self):
        self.layer = constants.LAYER_PLAYER
        skin_rect = pygame.rect.Rect(constants.CHARACTERS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * constants.SCALE_FACTOR for side in skin_rect.size])

    def change_facing(self, key):
        if key == pygame.K_RIGHT and not self.facing == constants.FACING_EAST:
            self.facing = constants.FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif key == pygame.K_LEFT and not self.facing == constants.FACING_WEST:
            self.facing = constants.FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def on_key_pressed(self, event_key, keys):
        magnitude = .7
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

    def move(self):
        super().move()
        self.apply_friction()


class Weapon(Sprite):
    STATIC = 0
    UP = 1
    DOWN = 2

    def __init__(self, surface, image, owner: Player):
        super().__init__()
        self.layer = constants.LAYER_WEAPON
        self.surface = surface
        self.original_image = image
        self.owner = owner
        self.sound = pygame.mixer.Sound(Path("assets/sounds/sfx/sword_brandishing.wav"))
        self.sound.set_volume(settings.SFX_VOLUME)

        weapon_rect = pygame.Rect(constants.BASIC_SWORD)
        self.image = self.original_image.subsurface(weapon_rect)
        self.image = pygame.transform.scale(self.image, [side * constants.ITEMS_SCALE_FACTOR for side in weapon_rect.size])
        self._image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center

        self.brandishing = Weapon.STATIC
        self.pivot = Vector2(self.rect.centerx, self.rect.centery + (self.rect.height // 2))
        self.rotation_vector = self.rect.center - self.pivot
        self.sword_angle = 0
        self.angle_diff = 0.5

    def update(self, *args, **kwargs):
        FACING = 1 if self.owner.facing == constants.FACING_EAST else -1
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
        if keys[pygame.K_SPACE] and self.alive() and self.brandishing == Weapon.STATIC:
            self.brandishing = Weapon.DOWN
            self.sound.play()
