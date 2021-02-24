from pathlib import Path
from functools import lru_cache
from typing import Tuple

import pygame
from pygame.math import Vector2

import constants


@lru_cache(maxsize=1)
def load_sprites_ui():
    return pygame.image.load(Path(constants.SPRITES_UI_PATH)).convert_alpha()


def ui_corner_scale(surface: pygame.Surface, scale_factor: int) -> Tuple[pygame.Surface, pygame.Rect]:
    surface = pygame.transform.scale(
        surface,
        [scale_factor * x for x in surface.get_size()]
    )
    return surface, surface.get_rect()


@lru_cache()
def ui_corner_top_left(scale_factor: int):
    return ui_corner_scale(load_sprites_ui().subsurface(constants.UI_BOX_CORNER_TOP_LEFT), scale_factor)


@lru_cache()
def ui_corner_bottom_left(scale_factor):
    return ui_corner_scale(load_sprites_ui().subsurface(constants.UI_BOX_CORNER_BOTTOM_LEFT), scale_factor)


@lru_cache()
def ui_corner_top_right(scale_factor):
    return ui_corner_scale(load_sprites_ui().subsurface(constants.UI_BOX_CORNER_TOP_RIGHT), scale_factor)


@lru_cache()
def ui_corner_bottom_right(scale_factor):
    return ui_corner_scale(load_sprites_ui().subsurface(constants.UI_BOX_CORNER_BOTTOM_RIGHT), scale_factor)


def ui_horizontal_bar_scale(surface, width, scale_factor):
    surface = pygame.transform.scale(
        surface,
        (
            width,
            surface.get_height() * scale_factor
        )
    )
    return surface, surface.get_rect()


@lru_cache()
def ui_bar_top(width, scale_factor):
    return ui_horizontal_bar_scale(load_sprites_ui().subsurface(constants.UI_BOX_TOP_HORIZONTAL_BAR), width, scale_factor)


@lru_cache()
def ui_bar_bottom(width, scale_factor):
    return ui_horizontal_bar_scale(load_sprites_ui().subsurface(constants.UI_BOX_BOTTOM_HORIZONTAL_BAR), width, scale_factor)


def ui_vertical_bar_scale(surface, height, scale_factor):
    surface = pygame.transform.scale(
        surface,
        (
            surface.get_width() * scale_factor,
            height,
        )
    )
    return surface, surface.get_rect()


@lru_cache()
def ui_vertical_bar_left(height, scale_factor):
    return ui_vertical_bar_scale(load_sprites_ui().subsurface(constants.UI_BOX_VERTICAL_BAR_LEFT), height, scale_factor)


@lru_cache()
def ui_vertical_bar_right(height, scale_factor):
    return ui_vertical_bar_scale(load_sprites_ui().subsurface(constants.UI_BOX_VERTICAL_BAR_RIGHT), height, scale_factor)


@lru_cache()
def ui_box_background():
    return load_sprites_ui().subsurface(constants.UI_BOX_BACKGROUND)


def build_frame(content_surface: pygame.Surface, rect: pygame.Rect,
                scale_factor: int = constants.UI_SCALE_FACTOR,
                padding: int = 10) -> Tuple[pygame.Surface, pygame.Rect]:
    """
    Given a surface, rect, and a scale factor, build a decorative frame on it.
    """
    content_width, content_height = rect.size
    # Pieces
    corner_top_left_surface, corner_top_left_rect = ui_corner_top_left(scale_factor)
    container_surface = pygame.Surface(
        (
            2 * (corner_top_left_rect.width + padding) + content_width,
            2 * (corner_top_left_rect.height + padding) + content_height
        ),
        flags=pygame.SRCALPHA
    )
    container_rect = container_surface.get_rect()

    corner_bottom_left_surface, corner_bottom_left_rect = ui_corner_bottom_left(scale_factor)
    corner_bottom_right_surface, corner_bottom_right_rect = ui_corner_bottom_right(scale_factor)
    corner_top_right_surface, corner_top_right_rect = ui_corner_top_right(scale_factor)

    horizontal_bar_width = container_rect.width - corner_top_left_rect.width * 2
    vertical_bar_height = container_rect.height - corner_bottom_left_rect.height - corner_top_left_rect.height

    bar_top_surface, bar_top_rect = ui_bar_top(horizontal_bar_width, scale_factor)
    bar_bottom_surface, bar_bottom_rect = ui_bar_bottom(horizontal_bar_width, scale_factor)
    bar_left_surface, bar_left_rect = ui_vertical_bar_left(vertical_bar_height, scale_factor)
    bar_right_surface, bar_right_rect = ui_vertical_bar_right(vertical_bar_height, scale_factor)

    background = pygame.Surface((
        container_rect.width - bar_right_rect.width * 2,
        container_rect.height - bar_top_rect.height - bar_bottom_rect.height
    ))
    background.fill(constants.UI_BOX_BACKGROUND_COLOR_PAPYRUS)

    container_surface.blits([
        (background, (bar_left_rect.right, bar_top_rect.bottom)),
        (corner_top_left_surface, (0, 0)),
        (corner_top_right_surface, (container_rect.right - corner_top_right_rect.width, 0)),
        (corner_bottom_left_surface, (0, container_rect.bottom - corner_bottom_left_rect.height)),
        (corner_bottom_right_surface, (
            container_rect.right - corner_bottom_right_rect.width,
            container_rect.bottom - corner_bottom_right_rect.height
        )),
        (bar_top_surface, (corner_top_left_rect.right, corner_top_left_rect.top)),
        (bar_bottom_surface, (corner_top_left_rect.right, container_rect.bottom - bar_bottom_rect.height)),
        (bar_left_surface, (0, corner_top_left_rect.bottom)),
        (bar_right_surface, (container_rect.right - bar_right_rect.width, corner_top_left_rect.bottom)),
        (content_surface, Vector2(container_rect.center) - Vector2(content_surface.get_size()) / 2),
    ])
    return container_surface, container_surface.get_rect()
