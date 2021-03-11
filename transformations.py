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
