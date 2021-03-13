import pygame
import numpy as np


def blur(surface: pygame.Surface, level: int) -> pygame.Surface:
    size = surface.get_size()
    scale_size = pygame.math.Vector2(size) / level
    surface = pygame.transform.smoothscale(surface, (int(scale_size.x), int(scale_size.y)))
    surface = pygame.transform.smoothscale(surface, size)
    return surface


def greyscale(surface: pygame.Surface):
    surface_copy = surface.copy()
    arr = pygame.surfarray.pixels3d(surface_copy)
    mean_arr = np.dot(arr, [0.216, 0.587, 0.144])
    arr[:, :, 0] = mean_arr
    arr[:, :, 1] = mean_arr
    arr[:, :, 2] = mean_arr
    return surface_copy


def redscale(surface: pygame.Surface):
    surface_copy = surface.copy()
    arr = pygame.surfarray.pixels3d(surface_copy)
    mean_arr = np.dot(arr, [0.216, 0.587, 0.144])
    original_shape = mean_arr.shape
    red_arr = np.copy(mean_arr)
    red_arr = red_arr.reshape(original_shape[0] * original_shape[1])
    red_arr = np.array([min(xi * 2, 255) for xi in red_arr])
    red_arr = red_arr.reshape(original_shape)
    arr[:, :, 0] = red_arr
    arr[:, :, 1] = mean_arr
    arr[:, :, 2] = mean_arr
    return surface_copy
