import os
import time
import random

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.math import Vector2

from constants import FACING_WEST, FACING_EAST, CHARACTERS, CHARACTERS_DICT, MOBS_DICT, GREEN_LIQUID_ITEM


class Item(Sprite):
    def __init__(self, surface, image, initial_position=(100, 100)):
        super().__init__()
        self.surface = surface
        self.original_image = image
        skin_rect = pygame.rect.Rect(GREEN_LIQUID_ITEM)
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * 4 for side in skin_rect.size])

        self.rect = self.image.get_rect()
        self.rect.center = initial_position

    def spawn(self, position=None):
        self.rect.center = Vector2(
            random.randint(100, self.surface.get_width() - 100),
            random.randint(100, self.surface.get_height() - 100)
        )


class Walker(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, skin='OLD_MAN', facing=FACING_EAST,
                 initial_position=(0, 0)):
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
        self.knock = pygame.mixer.Sound("assets/sounds/boundary_hit.ogg")

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
        if not 0 < self.center_position.x:
            self.center_position.x = 0
            self.velocity.x *= -1
            self.knock.play()
        elif not self.center_position.x < self.surface.get_width():
            self.center_position.x = self.surface.get_width()
            self.velocity.x *= -1
            self.knock.play()

        if not 0 < self.center_position.y:
            self.center_position.y = 0
            self.velocity.y *= -1
            self.knock.play()
        elif not self.center_position.y < self.surface.get_height():
            self.center_position.y = self.surface.get_height()
            self.velocity.y *= -1
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
        self.apply_force(distance_vector * 0.3 / (distance_vector.magnitude() * 10))
        self.move()
        self.bounce()
        self.change_facing()

    def set_skin(self):
        self.facing = FACING_WEST
        skin_rect = pygame.rect.Rect(MOBS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * 4 for side in skin_rect.size])


class Player(Walker):
    def set_skin(self):
        skin_rect = pygame.rect.Rect(CHARACTERS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * 4 for side in skin_rect.size])

    def next_skin(self):
        if time.time() - self.last_skin_change > 1:
            print("skin changed!")
            self.skin = CHARACTERS[(CHARACTERS.index(self.skin) + 1) % len(CHARACTERS)]
            self.set_skin()
            self.last_skin_change = time.time()

    def change_facing(self, key):
        if key == pygame.K_RIGHT and not self.facing == FACING_EAST:
            self.facing = FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif key == pygame.K_LEFT and not self.facing == FACING_WEST:
            self.facing = FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def on_key_pressed(self, key):
        magnitude = .5
        if key == pygame.K_RIGHT:
            self.apply_force(Vector2(magnitude, 0))
        elif key == pygame.K_LEFT:
            self.apply_force(Vector2(-magnitude, 0))
        elif key == pygame.K_UP:
            self.apply_force(Vector2(0, -magnitude))
        elif key == pygame.K_DOWN:
            self.apply_force(Vector2(0, magnitude))
        elif key == pygame.K_s:
            self.next_skin()

        self.change_facing(key)

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()


class Score(Sprite):
    def __init__(self, surface):
        super().__init__()
        self.surface = surface
        # upper left corner with a font size of 64
        # the number 200 for the width is arbitrary
        self.fnt = pygame.freetype.Font("./assets/fonts/quicksand.ttf", 32)  # FIXME: adjust size
        self.value = 0

    def update(self, *args, **kwargs) -> None:
        self.image, self.rect = self.fnt.render(f"Score: {self.value}", pygame.color.Color("white"))
        self.rect.center = [(self.rect.width / 2) + 5, (self.rect.height / 2) + 5]


class Option(Sprite):
    def __init__(self, surface: pygame.Surface, text: str):
        super().__init__()
        self.text = text
        self.surface = surface
        self.fnt = pygame.freetype.Font("./assets/fonts/young_serif_regular.otf", 62)
        self.fnt.underline_adjustment = 1
        self.fnt.pad = True

    def render(self, *args, **kwargs):
        self.image, _ = self.fnt.render(text=self.text, fgcolor=pygame.color.Color("white"))
        self.rect = self.image.get_rect()

    def select(self):
        self.fnt.underline = True

    def unselect(self):
        self.fnt.underline = False


class MainMenu(Sprite):
    START = 0
    QUIT = 1

    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.selected_option = MainMenu.START
        self.start_option = Option(surface, text="Start")
        self.quit_option = Option(surface, text="Quit")
        self.options = [
            self.start_option,
            self.quit_option,
        ]
        self.image = pygame.Surface((0, 32 * len(self.options)))
        self.render()

    def render(self):
        # Underlining selected option
        for opt in self.options:
            opt.fnt.underline = False
        self.options[self.selected_option].fnt.underline = True

        # Adjusting next rect position
        last_y_position = 0
        for opt in self.options:
            opt.render()  # calculates how to render the text
            opt.rect.y += last_y_position
            last_y_position += opt.rect.height

        # Blitting into self.image
        self.rect = self.image.get_rect().unionall([opt.rect for opt in self.options])
        self.rect.center = self.surface.get_rect().center
        self.image = pygame.surface.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.blits([(opt.image, opt.rect) for opt in self.options])

    def next_option(self):
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self.render()
