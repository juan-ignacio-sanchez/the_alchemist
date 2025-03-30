import time
from enum import IntEnum
from pathlib import Path
import logging

import pygame
import pygame.freetype
from pygame.sprite import Sprite
from pygame.transform import scale

import settings
from constants import (
    FONT_PATH_HELPER,
    FONT_PATH_MAIN,
    FONT_PATH_PAUSED,
    FONT_PATH_SECONDARY,
    SFX_MENU_ITEM_CHANGED,
    UI_BOX_TEXT_COLOR_PAPYRUS,
    UI_BOX_BACKGROUND_COLOR_PAPYRUS,
)
from .images import build_frame

logger = logging.getLogger()


class Score(Sprite):
    # TODO: This class might evolve into a GameState class
    def __init__(self, surface, max_score, seconds_to_leave=3):
        super().__init__()
        self.surface = surface
        # upper left corner with a font size of 64
        # the number 200 for the width is arbitrary
        self.fnt = pygame.freetype.Font(FONT_PATH_MAIN, 12)  # FIXME: adjust size
        self.fnt.pad = True
        self.value = 0
        self.max_score = max_score
        self.win_timestamp = None
        self.seconds_to_leave = seconds_to_leave
        self.transition_seconds = 1
        self.hidden = False
        self.image, self.rect = self.render_surface()

    def quit_transition(self):
        if self.win_timestamp:
            return (
                self.seconds_to_leave - self.transition_seconds
                <= (time.time() - self.win_timestamp)
                <= self.seconds_to_leave
            )
        else:
            return False

    def is_time_to_leave(self):
        if self.win_timestamp:
            return (time.time() - self.win_timestamp) >= self.seconds_to_leave
        else:
            return False

    def won(self):
        return self.value == self.max_score

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def increase(self, amount=1):
        self.value += 1
        if self.value == self.max_score:
            self.win_timestamp = time.time()

    def render_surface(self):
        score_surface, score_rect = self.fnt.render(
            f"Potions left: {self.max_score - self.value}",
            pygame.color.Color(UI_BOX_TEXT_COLOR_PAPYRUS),
        )
        score_rect.center = [(score_rect.width / 2) + 5, (score_rect.height / 2) + 5]
        return build_frame(score_surface, score_rect)

    def update(self, *args, **kwargs) -> None:
        self.image, self.rect = self.render_surface()
        if self.hidden:
            self.image.set_alpha(50)


class Option(Sprite):
    def __init__(
        self, surface: pygame.Surface, text: str, size: int = 62, interlined=0
    ):
        super().__init__()
        self.text = text
        self.surface = surface
        self.fnt = pygame.freetype.Font(FONT_PATH_MAIN, size)
        self.fnt.underline_adjustment = 1
        self.fnt.pad = True
        self.interlined = interlined

    def render(self, *args, **kwargs):
        self.image, _ = self.fnt.render(
            text=self.text, fgcolor=pygame.color.Color("white")
        )
        self.rect = self.image.get_rect()
        self.rect.height += self.interlined

    def select(self):
        self.fnt.underline = True

    def unselect(self):
        self.fnt.underline = False


class MainMenu(Sprite):
    options = IntEnum(
        "options",
        (
            "START",
            "CONTROLS",
            "CREDITS",
            "QUIT",
        ),
        start=0,
    )

    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.title = Option(surface, text="~ The Alchemist ~", size=70, interlined=70)
        self.option_change_sound = pygame.mixer.Sound(Path(SFX_MENU_ITEM_CHANGED))
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


class Banner(Sprite):
    def __init__(self, screen: pygame.Surface, main_text, secondary_text):
        super().__init__()
        self.main_text = main_text
        self.secondary_text = secondary_text
        self.screen = screen
        self.main_fnt = pygame.freetype.Font(FONT_PATH_MAIN, 52)
        self.main_fnt.pad = True
        self.secondary_fnt = pygame.freetype.Font(FONT_PATH_SECONDARY, 22)

    def update(self, *args, **kwargs):
        main_surface, _ = self.main_fnt.render(
            text=self.main_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        main_rect = main_surface.get_rect()

        secondary_surface, _ = self.secondary_fnt.render(
            text=self.secondary_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        secondary_rect = main_rect.copy()
        secondary_rect.y += secondary_rect.height

        self.image = pygame.surface.Surface(
            main_rect.union(secondary_rect).size, flags=pygame.SRCALPHA
        )

        main_rect.centerx = self.image.get_rect().centerx
        secondary_rect.centerx = main_rect.centerx

        self.image.blits(
            [
                (main_surface, main_rect),
                (secondary_surface, secondary_rect),
            ]
        )
        self.rect = self.image.get_rect()

        # self.image, self.rect = build_frame(self.image, self.rect)
        self.rect.center = self.screen.get_rect().center


class EphemeralBanner(Banner):
    def __init__(self, expiration, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.creation = time.time()
        self.expiration = expiration

    def update(self, *args, **kwargs):
        super().update()
        if time.time() - self.creation >= self.expiration:
            self.kill()


class EphemeralVisualEffect(Sprite):
    def __init__(self, screen, image, expiration, *args, **kwargs):
        super().__init__(*args)
        self.screen = screen
        self.image = scale(image, screen.get_size())
        self.rect = image.get_rect()
        self.creation = time.time()
        self.expiration = expiration

    def update(self, *args, **kwargs):
        super().update()
        if time.time() - self.creation >= self.expiration:
            self.kill()


class PlayerKilledBanner(Sprite):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.main_text = "Mastering alchemy is not that easy!"
        self.secondary_text = "Press R to restart, or ESC to exit"
        self.screen = screen
        self.main_fnt = pygame.freetype.Font(FONT_PATH_MAIN, 52)
        self.secondary_fnt = pygame.freetype.Font(FONT_PATH_SECONDARY, 22)
        self.main_fnt.pad = self.secondary_fnt.pad = True

    def update(self, *args, **kwargs):
        main_surface, _ = self.main_fnt.render(
            text=self.main_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        main_rect = main_surface.get_rect()

        secondary_surface, _ = self.secondary_fnt.render(
            text=self.secondary_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        secondary_rect = main_surface.get_rect()
        secondary_rect.y += main_rect.height

        self.image = pygame.surface.Surface(
            main_rect.union(secondary_rect).size, flags=pygame.SRCALPHA
        )

        main_rect.centerx = self.image.get_rect().centerx
        secondary_rect.centerx = main_rect.centerx

        self.image.blits(
            [
                (main_surface, main_rect),
                (secondary_surface, secondary_rect),
            ]
        )
        self.rect = self.image.get_rect()
        self.rect.center = self.screen.get_rect().center


class PauseBanner(Sprite):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.paused_text = "Paused"
        self.helper_text = "Press P to resume"
        self.screen = screen
        try:
            self.paused_fnt = pygame.freetype.Font(FONT_PATH_PAUSED, 62)
            self.helper_fnt = pygame.freetype.Font(FONT_PATH_HELPER, 32)
        except OSError:
            logger.exception("Pause Banner fonts failed to load. %s" % FONT_PATH_PAUSED)
        except Exception:
            logger.exception("Unknown Exception while loading fonts for Pause Banner.")
        self.paused_fnt.pad = self.helper_fnt.pad = True
        self.output_surface = None
        self.output_rect = None

    def render(self, *args, **kwargs):
        paused_surface, _ = self.paused_fnt.render(
            text=self.paused_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        paused_rect = paused_surface.get_rect()

        helper_surface, _ = self.helper_fnt.render(
            text=self.helper_text,
            fgcolor=pygame.color.Color(UI_BOX_BACKGROUND_COLOR_PAPYRUS),
        )
        helper_rect = helper_surface.get_rect()
        helper_rect.y += paused_rect.height

        self.output_surface = pygame.surface.Surface(
            paused_rect.union(helper_rect).size, flags=pygame.SRCALPHA
        )

        paused_rect.centerx = self.output_surface.get_rect().centerx
        helper_rect.centerx = paused_rect.centerx

        self.output_surface.blits(
            [
                (paused_surface, paused_rect),
                (helper_surface, helper_rect),
            ]
        )
        self.output_rect = self.output_surface.get_rect()
        self.output_rect.center = self.screen.get_rect().center

        return self.output_surface, self.output_rect
