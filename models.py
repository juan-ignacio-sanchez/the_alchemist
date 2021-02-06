import time
import random
from enum import IntEnum
from pathlib import Path

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.math import Vector2

import settings
from constants import FACING_WEST, FACING_EAST, CHARACTERS_DICT, MOBS_DICT, WIDE_GREEN_LIQUID_ITEM


class Item(Sprite):
    def __init__(self, surface, image, initial_position=(100, 100)):
        super().__init__()
        self.surface = surface
        self.original_image = image
        skin_rect = pygame.rect.Rect(WIDE_GREEN_LIQUID_ITEM)
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
        self.knock = pygame.mixer.Sound(Path("assets/sounds/boundary_hit.ogg"))

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
        self.image = pygame.transform.scale(self.image, [side * 5 for side in skin_rect.size])


class Player(Walker):
    def set_skin(self):
        skin_rect = pygame.rect.Rect(CHARACTERS_DICT.get(self.skin))
        self.image = self.original_image.subsurface(skin_rect)
        self.image = pygame.transform.scale(self.image, [side * 5 for side in skin_rect.size])

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


class Score(Sprite):
    def __init__(self, surface):
        super().__init__()
        self.surface = surface
        # upper left corner with a font size of 64
        # the number 200 for the width is arbitrary
        self.fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 32)  # FIXME: adjust size
        self.value = 0

    def update(self, *args, **kwargs) -> None:
        self.image, self.rect = self.fnt.render(f"Score: {self.value}", pygame.color.Color("white"))
        self.rect.center = [(self.rect.width / 2) + 5, (self.rect.height / 2) + 5]


class Option(Sprite):
    def __init__(self, surface: pygame.Surface, text: str, size: int = 62, interlined=0):
        super().__init__()
        self.text = text
        self.surface = surface
        self.fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), size)
        self.fnt.underline_adjustment = 1
        self.fnt.pad = True
        self.interlined = interlined

    def render(self, *args, **kwargs):
        self.image, _ = self.fnt.render(text=self.text, fgcolor=pygame.color.Color("white"))
        self.rect = self.image.get_rect()
        self.rect.height += self.interlined

    def select(self):
        self.fnt.underline = True

    def unselect(self):
        self.fnt.underline = False


class MainMenu(Sprite):
    options = IntEnum('options', (
        'START',
        'CONTROLS',
        'CREDITS',
        'QUIT',
    ), start=0)

    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.title = Option(surface, text="~ The Alchemist ~", size=70, interlined=70)
        self.option_change_sound = pygame.mixer.Sound(Path('./assets/sounds/menu_item_changed.ogg'))
        self.option_change_sound.set_volume(settings.VOLUME)
        self.selected_option = MainMenu.options.START
        self.options = [
            Option(surface, text="NEW GAME"),
            Option(surface, text="CONTROLS"),
            Option(surface, text="CREDITS"),
            Option(surface, text="QUIT"),
        ]
        self.image = pygame.Surface((0, 32 * len(self.options)))
        self.render()

    def render(self):
        # Underlining selected option
        for opt in self.options:
            opt.fnt.underline = False
        self.options[self.selected_option].fnt.underline = True

        all_texts = [self.title] + self.options
        # Adjusting next rect position
        last_y_position = 50
        for opt in all_texts:
            opt.render()  # calculates how to render the text
            opt.rect.y += last_y_position
            opt.rect.centerx = self.surface.get_width() / 2
            last_y_position += opt.rect.height

        # Blitting into self.image
        self.rect = self.image.get_rect().unionall([opt.rect for opt in all_texts])
        self.image = pygame.surface.Surface(self.rect.size, flags=pygame.SRCALPHA)
        self.image.blits([(opt.image, opt.rect) for opt in all_texts])

    def prev_option(self) -> int:
        self.selected_option = (self.selected_option - 1) % len(self.options)
        self.render()
        self.option_change_sound.play()
        return self.selected_option

    def next_option(self) -> int:
        self.selected_option = (self.selected_option + 1) % len(self.options)
        self.render()
        self.option_change_sound.play()
        return self.selected_option


class PlayerKilledBanner(Sprite):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.main_text = "Mastering alchemy is not that easy!"
        self.secondary_text = "Press R to restart, or ESC to exit"
        self.screen = screen
        self.main_fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 52)
        self.secondary_fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 22)
        self.main_fnt.pad = self.secondary_fnt.pad = True

    def update(self, *args, **kwargs):
        main_surface, _ = self.main_fnt.render(text=self.main_text, fgcolor=pygame.color.Color("white"))
        main_rect = main_surface.get_rect()

        secondary_surface, _ = self.secondary_fnt.render(text=self.secondary_text, fgcolor=pygame.color.Color("white"))
        secondary_rect = main_surface.get_rect()
        secondary_rect.y += main_rect.height

        self.image = pygame.surface.Surface(main_rect.union(secondary_rect).size, flags=pygame.SRCALPHA)

        main_rect.centerx = self.image.get_rect().centerx
        secondary_rect.centerx = main_rect.centerx

        self.image.blits([
            (main_surface, main_rect),
            (secondary_surface, secondary_rect),
        ])
        self.rect = self.image.get_rect()
        self.rect.center = self.screen.get_rect().center


class PauseBanner(Sprite):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.paused_text = "Paused"
        self.helper_text = "Press P to resume"
        self.screen = screen
        self.paused_fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 62)
        self.helper_fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 32)
        self.paused_fnt.pad = self.helper_fnt.pad = True
        self.output_surface = None
        self.output_rect = None

    def render(self, *args, **kwargs):
        paused_surface, _ = self.paused_fnt.render(text=self.paused_text, fgcolor=pygame.color.Color("white"))
        paused_rect = paused_surface.get_rect()

        helper_surface, _ = self.helper_fnt.render(text=self.helper_text, fgcolor=pygame.color.Color("white"))
        helper_rect = helper_surface.get_rect()
        helper_rect.y += paused_rect.height

        self.output_surface = pygame.surface.Surface(paused_rect.union(helper_rect).size, flags=pygame.SRCALPHA)

        paused_rect.centerx = self.output_surface.get_rect().centerx
        helper_rect.centerx = paused_rect.centerx

        self.output_surface.blits([
            (paused_surface, paused_rect),
            (helper_surface, helper_rect),
        ])
        self.output_rect = self.output_surface.get_rect()
        self.output_rect.center = self.screen.get_rect().center

        return self.output_surface, self.output_rect
