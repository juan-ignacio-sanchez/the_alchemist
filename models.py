import time
import random
from enum import IntEnum
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


class Score(Sprite):
    # TODO: This class might evolve into a GameState class
    def __init__(self, surface, max_score, seconds_to_leave=3):
        super().__init__()
        self.surface = surface
        # upper left corner with a font size of 64
        # the number 200 for the width is arbitrary
        self.fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 32)  # FIXME: adjust size
        self.value = 0
        self.max_score = max_score
        self.win_timestamp = None
        self.seconds_to_leave = seconds_to_leave
        self.transition_seconds = 1

    def quit_transition(self):
        if self.win_timestamp:
            return self.seconds_to_leave - self.transition_seconds <= (time.time() - self.win_timestamp) <= self.seconds_to_leave
        else:
            return False

    def is_time_to_leave(self):
        if self.win_timestamp:
            return (time.time() - self.win_timestamp) >= self.seconds_to_leave
        else:
            return False

    def won(self):
        return self.value == self.max_score

    def increase(self, amount=1):
        self.value += 1
        if self.value == self.max_score:
            self.win_timestamp = time.time()

    def update(self, *args, **kwargs) -> None:
        self.image, self.rect = self.fnt.render(f"Potions left: {self.max_score - self.value}", pygame.color.Color("white"))
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
        self.option_change_sound = pygame.mixer.Sound(Path(MENU_ITEM_CHANGED_SFX))
        self.option_change_sound.set_volume(settings.SFX_VOLUME)
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


class PlayerWonBanner(Sprite):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.main_text = "You Win!"
        self.screen = screen
        self.main_fnt = pygame.freetype.Font(Path("./assets/fonts/young_serif_regular.otf"), 72)
        self.main_fnt.pad = True

    def update(self, *args, **kwargs):
        main_surface, _ = self.main_fnt.render(text=self.main_text, fgcolor=pygame.color.Color("white"))
        main_rect = main_surface.get_rect()

        self.image = pygame.surface.Surface(main_rect.size, flags=pygame.SRCALPHA)

        main_rect.centerx = self.image.get_rect().centerx

        self.image.blits([
            (main_surface, main_rect),
        ])
        self.rect = self.image.get_rect()
        self.rect.center = self.screen.get_rect().center


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
            if self.sword_angle >= 90:
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
