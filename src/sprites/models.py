import time
import random
import logging
from pathlib import Path
from math import copysign
from typing import Tuple

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.math import Vector2

import settings
import constants
from sprites.images import load_sprites, load_player_walking
from transformations import greyscale, redscale, slice_into_particles

logger = logging.getLogger(__name__)


class Item(Sprite):
    RED = constants.POTION_RED
    BLUE = constants.POTION_BLUE
    GREEN = constants.POTION_GREEN

    def __init__(self, surface, image, color, initial_position=(100, 100)):
        super().__init__()
        self.layer = constants.LAYER_ITEM
        self.surface = surface
        self.original_image = image

        self.color = color
        skin_rect = pygame.Rect(constants.POTION_COLORS[color])
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(
            self.image, [side * constants.ITEMS_SCALE_FACTOR for side in skin_rect.size]
        )
        self.rect = self.image.get_rect()
        self.spawn(initial_position)

    def spawn(self, color=None, position=None):
        if not position:
            self.rect.center = Vector2(
                random.randint(100, self.surface.get_width() - 100),
                random.randint(100, self.surface.get_height() - 100),
            )
        else:
            self.rect.center = position


class Particle(Sprite):
    def __init__(
        self,
        surface: pygame.Surface,
        image: pygame.Surface,
        initial_position: Tuple = (50, 50),
        reference_force_vector: Vector2 = None,
    ):
        super().__init__()
        self.layer = constants.LAYER_PARTICLE
        self.surface = surface

        self.image = image

        self.initial_position = Vector2(initial_position)
        self.decay_distance = random.choice(
            (*([random.randint(100, 200)] * 10), random.randint(250, 400))
        )
        self.rect = self.image.get_rect()
        self.rect.center = initial_position

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        angle = random.randint(-15000, 15000)
        magnitude = random.choice(
            (*([random.randint(10, 100)] * 5), random.randint(100, 2500))
        )
        magnitude /= 1000
        self.force_to_apply = reference_force_vector.rotate(angle / 1000) * magnitude

    def apply_force(self, force: Vector2):
        self.acceleration += force

    def apply_friction(self):
        if self.velocity.magnitude():
            friction_force = self.velocity * -0.99
            self.apply_force(friction_force)

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration.update(0, 0)

    def update(self, *args, **kwargs) -> None:
        self.apply_force(self.force_to_apply)
        self.apply_friction()
        self.move()
        if (
            not self.surface.get_rect().contains(self.rect)
            or self.initial_position.distance_to(self.center_position)
            > self.decay_distance
        ):
            self.kill()


class Walker(Sprite):
    def __init__(
        self,
        surface: pygame.Surface,
        skin=constants.PLAYER_OLD_MAN,
        facing=constants.FACING_EAST,
        initial_position=(50, 50),
        skin_source=None,
        image_sequence=None,
        loader=load_sprites,
    ):
        super().__init__()
        self.surface = surface

        # Skin related stuff
        self.image_sequence = image_sequence or list(skin_source.values())
        self.last_skin_change = 0
        self.current_image = 0
        self.skin_source = skin_source
        self.skin = skin
        self.original_image = loader()
        self.facing = facing
        self.set_skin()

        self.initial_position = initial_position
        self.rect = self.image.get_rect()
        self.rect.center = initial_position
        self._image = self.image.copy()

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Sound
        self.knock = pygame.mixer.Sound(Path(constants.SFX_WALL_HIT))
        self.knock.set_volume(settings.SFX_VOLUME)
        self.footsteps = pygame.mixer.Sound(Path(constants.SFX_FOOTSTEPS))
        self.footsteps.set_volume(settings.SFX_VOLUME)

    def next_image(self):
        self.current_image = (self.current_image + 1) % 2
        return self.image_sequence[self.current_image]

    def restore_initial_position(self):
        self.velocity.update(0, 0)
        self.acceleration.update(0, 0)
        self.center_position.update(self.initial_position)
        self.rect.center = self.center_position

    def set_skin(self):
        if time.time() - self.last_skin_change > 0.2:
            self.last_skin_change = time.time()
            skin_rect = pygame.rect.Rect(self.skin_source.get(self.skin))
            self.image = self.original_image.subsurface(self.next_image())
            self.image = pygame.transform.scale(
                self.image, [side * constants.SCALE_FACTOR for side in skin_rect.size]
            )
            if self.facing == constants.FACING_WEST:
                self.image = pygame.transform.flip(self.image, True, False)

    def apply_force(self, force: Vector2):
        self.acceleration += force

    def apply_gravity(self):
        self.apply_force(Vector2(0, 0.002))

    def apply_friction(self):
        if self.velocity.magnitude():
            friction_force = self.velocity * -0.10
            self.apply_force(friction_force)

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration = Vector2(0, 0)

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

    def __init__(self, *args, particles_group, **kwargs):
        super().__init__(*args, skin_source=constants.MOBS_DICT, **kwargs)
        self.layer = constants.LAYER_ENEMY
        self.banishing_sound = pygame.mixer.Sound(Path(constants.SFX_ENEMY_KILLED))
        self.banishing_sound.set_volume(settings.SFX_VOLUME)
        self.hearts = 3
        self.last_hit = time.time()
        self._back_to_normal = False
        # Change style of image
        self.image_state = self.IMAGE_STATE_NORMAL
        self._image = self.image.copy()
        self.restore_image = False
        self.last_player_position = Vector2(1, 0)
        self.particles_group = particles_group

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

    def hurt(self, player_position: Vector2, hearts: int = 1):
        if not self.being_repeled():
            self.hearts -= 1
            self.apply_force(-self.velocity)
            self.apply_force((self.center_position - player_position).normalize() * 15)
            self.last_hit = time.time_ns()
            self.image = redscale(self.image)
            self.image_state = self.IMAGE_STATE_HURT
            self.last_player_position.update(player_position)
            print(
                "Before entering slice_into_particles",
                self._image,
                self.rect,
                self.center_position - player_position,
            )
            particles = slice_into_particles(
                self._image,
                rect=self.rect,
                size=3,
                skip=4,
                coloring=redscale,
                particle_class=Particle,
                surface=self.surface,
                reference_force_vector=self.center_position - player_position,
            )
            self.particles_group.add(particles)

    def update_image_state(self):
        if self.image_state == self.IMAGE_STATE_HURT and not self.being_repeled():
            self.image_state = self.IMAGE_STATE_BACK_TO_NORMAL
        if self.hearts <= 0 and not self.being_repeled():
            return self.die(self.last_player_position)

    def die(self, player_position: Vector2):
        PIECE_SIZE = 3

        SKIP = 1
        self.kill()
        self.banishing_sound.play()
        # Slice squares the image apart.
        x_slices = self.rect.width // PIECE_SIZE
        y_slices = self.rect.height // PIECE_SIZE
        height = PIECE_SIZE
        width = PIECE_SIZE

        image = self._image.copy()
        particles = []
        for slice_x_position in range(0, x_slices, SKIP):
            vertical_offset = 0
            for slice in range(0, y_slices, SKIP):
                subsurf = image.subsurface(
                    slice_x_position * width, vertical_offset, width, height
                )
                x, y = subsurf.get_offset()
                particles.append(
                    Particle(
                        surface=self.surface,
                        image=subsurf,
                        initial_position=(self.rect.x + x, self.rect.y + y),
                        reference_force_vector=self.center_position - player_position,
                    )
                )
                vertical_offset += height * SKIP

        if self.particles_group is not None:
            self.particles_group.add(particles)

    def update(self, *args, **kwargs) -> None:
        player_position = Vector2(kwargs.get("player_position"))
        # Follow the player
        distance_vector = Vector2(player_position - self.center_position)
        distance_vector.scale_to_length(distance_vector.magnitude())
        force = self.limit_vector(distance_vector, 0.005, 0.1)

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


class Player(Walker):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            image_sequence=constants.PLAYER_WALKING_SEQUENCE,
            skin_source=constants.PLAYER_DICT,
            loader=load_player_walking,
            **kwargs,
        )
        self.layer = constants.LAYER_PLAYER
        self.direction = Vector2(0, 0)
        self.walking = False

    def change_facing(self, horizontal_direction):
        if horizontal_direction > 0 and not self.facing == constants.FACING_EAST:
            logger.debug("Should flip facing EAST")
            self.facing = constants.FACING_EAST

        if horizontal_direction <= 0 and not self.facing == constants.FACING_WEST:
            logger.debug("Should flip facing WEST")
            self.facing = constants.FACING_WEST

    def on_key_pressed(self, event_key, keys):
        if not self.walking:
            self.walking = True
            self.footsteps.play()
        if event_key == settings.KEY_RIGHT:
            self.direction += (1, 0)
            self.change_facing(self.direction.x)
        if event_key == settings.KEY_LEFT:
            self.direction += (-1, 0)
            self.change_facing(self.direction.x)
        if event_key == settings.KEY_UP:
            self.direction += (0, -1)
        if event_key == settings.KEY_DOWN:
            self.direction += (0, 1)

    def on_key_released(self, event_key, keys):
        if event_key in [settings.KEY_RIGHT, settings.KEY_LEFT]:
            self.direction.update(0, self.direction.y)

        if event_key in [settings.KEY_UP, settings.KEY_DOWN]:
            self.direction.update(self.direction.x, 0)

        if self.walking and self.direction == (0, 0):
            self.walking = False
            self.footsteps.stop()
            self.velocity.update(0, 0)
            self.acceleration.update(0, 0)

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()

    def move(self):
        magnitude = 1.5
        if self.direction.magnitude() > 0:
            self.set_skin()
            self.apply_force(self.direction.normalize() * magnitude)
        self.apply_friction()
        super().move()


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
        self.sound = pygame.mixer.Sound(constants.SFX_SWORD_BRANDISHING)
        self.sound.set_volume(settings.SFX_VOLUME)

        weapon_rect = pygame.Rect(constants.BASIC_SWORD)
        self.image = self.original_image.subsurface(weapon_rect)
        self.image = pygame.transform.scale(
            self.image,
            [side * constants.ITEMS_SCALE_FACTOR for side in weapon_rect.size],
        )
        self._image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.center = owner.rect.center

        self.brandishing = Weapon.STATIC
        self.pivot = Vector2(
            self.rect.centerx, self.rect.centery + (self.rect.height // 2)
        )
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
