from pathlib import Path
from functools import lru_cache
from typing import Tuple

import pygame
from pygame.math import Vector2

import constants


@lru_cache()
def load_sprites_ui():
    return pygame.image.load(Path("./assets/sprites/sprites_ui.png")).convert_alpha()


@lru_cache()
def ui_left_top_corner():
    return load_sprites_ui().subsurface(constants.UI_BOX_CORNER_UP_LEFT)


@lru_cache()
def ui_right_top_corner():
    return load_sprites_ui().subsurface(constants.UI_BOX_CORNER_UP_RIGHT)


@lru_cache()
def ui_right_bottom_corner():
    return load_sprites_ui().subsurface(constants.UI_BOX_CORNER_BOTTOM_RIGHT)


@lru_cache()
def ui_top_bar():
    return load_sprites_ui().subsurface(constants.UI_BOX_TOP_HORIZONTAL_BAR)


@lru_cache()
def ui_bottom_bar():
    return load_sprites_ui().subsurface(constants.UI_BOX_BOTTOM_HORIZONTAL_BAR)


@lru_cache()
def ui_left_bottom_corner():
    return load_sprites_ui().subsurface(constants.UI_BOX_CORNER_BOTTOM_LEFT)


@lru_cache()
def ui_left_vertical_bar():
    return load_sprites_ui().subsurface(constants.UI_BOX_VERTICAL_BAR_LEFT)


@lru_cache()
def ui_right_vertical_bar():
    return load_sprites_ui().subsurface(constants.UI_BOX_VERTICAL_BAR_RIGHT)


@lru_cache()
def ui_box_background():
    return load_sprites_ui().subsurface(constants.UI_BOX_BACKGROUND)


def build_frame(surface: pygame.Surface, rect: pygame.Rect,
                scale_factor: int = constants.ITEMS_SCALE_FACTOR,
                padding: int = 10) -> Tuple[pygame.Surface, pygame.Rect]:
    """Given a surface, rect, and a scale factor, build a decorative frame on it."""
    content_width, content_height = rect.size
    # Pieces
    left_up_corner_surface = pygame.transform.scale(
        ui_left_top_corner(),
        [scale_factor * x for x in ui_left_top_corner().get_rect()[2:]]
    )
    left_up_corner_rect = left_up_corner_surface.get_rect()
    total_padding = padding + left_up_corner_rect.width
    container_surface = pygame.Surface(
        (
            2 * (left_up_corner_rect.width + padding) + content_width,
            2 * (left_up_corner_rect.height + padding) + content_height
        ),
        flags=pygame.SRCALPHA
    )
    container_width, container_height = container_surface.get_size()

    top_bar_surface = pygame.transform.scale(
        ui_top_bar(),
        (
            container_surface.get_width() - left_up_corner_rect.width * 2,
            ui_top_bar().get_height() * scale_factor
        )
    )
    bottom_bar_surface = pygame.transform.scale(
        ui_bottom_bar(),
        (
            container_surface.get_width() - left_up_corner_rect.width * 2,
            ui_bottom_bar().get_height() * scale_factor
        )
    )
    bottom_left_corner_surface = pygame.transform.scale(
        ui_left_bottom_corner(),
        [scale_factor * x for x in ui_left_bottom_corner().get_rect()[2:]]
    )
    bottom_right_corner_surface = pygame.transform.scale(
        ui_right_bottom_corner(),
        [scale_factor * x for x in ui_right_bottom_corner().get_rect()[2:]]
    )
    top_right_corner_surface = pygame.transform.scale(
        ui_right_top_corner(),
        [scale_factor * x for x in ui_right_top_corner().get_rect()[2:]]
    )
    vertical_left_surface = pygame.transform.scale(
        ui_left_vertical_bar(),
        (
            ui_left_vertical_bar().get_width() * scale_factor,
            container_surface.get_height() - bottom_left_corner_surface.get_height() - left_up_corner_rect.height
        )
    )
    vertical_right_surface = pygame.transform.scale(
        ui_right_vertical_bar(),
        (
            ui_right_vertical_bar().get_width() * scale_factor,
            container_surface.get_height() - bottom_left_corner_surface.get_height() - left_up_corner_rect.height
        )
    )

    background = pygame.Surface((
        container_width - vertical_right_surface.get_width() * 2,
        container_height - top_bar_surface.get_height() - bottom_bar_surface.get_height()
    ))
    background.fill(constants.UI_BOX_BACKGROUND_COLOR_PAPYRUS)

    container_surface.blits([
        (background, (vertical_left_surface.get_rect().right, top_bar_surface.get_rect().bottom)),
        (left_up_corner_surface, (0, 0)),
        (top_bar_surface, (left_up_corner_rect.right, left_up_corner_rect.top)),
        (vertical_left_surface, (0, left_up_corner_rect.bottom)),
        (vertical_right_surface, (container_surface.get_rect().right - vertical_right_surface.get_rect().width, left_up_corner_rect.bottom)),
        (bottom_left_corner_surface, (0, container_surface.get_rect().bottom - bottom_left_corner_surface.get_height())),
        (bottom_right_corner_surface, (container_surface.get_rect().right - bottom_right_corner_surface.get_width(), container_surface.get_rect().bottom - bottom_right_corner_surface.get_height())),
        (top_right_corner_surface, (container_surface.get_rect().right - top_right_corner_surface.get_width(), 0)),
        (bottom_bar_surface, (left_up_corner_rect.right, container_surface.get_rect().bottom - bottom_bar_surface.get_height())),
        (surface, Vector2(container_surface.get_rect().center) - Vector2(surface.get_size())/2),
    ])
    return container_surface, container_surface.get_rect()
