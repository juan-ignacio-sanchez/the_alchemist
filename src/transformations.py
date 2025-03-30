import numpy as np

import pygame
from pygame.math import Vector2


def blur(surface: pygame.Surface, level: float) -> pygame.Surface:
    size = surface.get_size()
    scale_size = pygame.math.Vector2(size) / level
    surface = pygame.transform.smoothscale(
        surface, (int(scale_size.x), int(scale_size.y))
    )
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


def redscale(surface: pygame.Surface, intensity=2):
    surface_copy = surface.copy()
    arr = pygame.surfarray.pixels3d(surface_copy)
    mean_arr = np.dot(arr, [0.216, 0.587, 0.144])
    original_shape = mean_arr.shape
    red_arr = np.copy(mean_arr)
    red_arr = red_arr.reshape(original_shape[0] * original_shape[1])
    red_arr = np.array([min(xi * intensity, 255) for xi in red_arr])
    red_arr = red_arr.reshape(original_shape)
    arr[:, :, 0] = red_arr
    arr[:, :, 1] = mean_arr
    arr[:, :, 2] = mean_arr
    return surface_copy


def slice_into_particles(
    image: pygame.Surface,
    rect: pygame.Rect,
    size: int,
    skip: int,
    particle_class: callable,
    surface: pygame.Surface,
    coloring: callable = lambda x: x,
    reference_force_vector: pygame.Vector2 = None,
):
    # Slice squares the image apart.
    x_slices = rect.width // size
    y_slices = rect.height // size
    height = size
    width = size

    image = coloring(image.copy())
    particles = []
    for slice_x_position in range(0, x_slices, skip):
        vertical_offset = 0
        for slice in range(0, y_slices, skip):
            subsurf = image.subsurface(
                slice_x_position * width, vertical_offset, width, height
            )
            x, y = subsurf.get_offset()
            particles.append(
                particle_class(
                    surface=surface,
                    image=subsurf,
                    initial_position=(rect.x + x, rect.y + y),
                    reference_force_vector=reference_force_vector,
                )
            )
            vertical_offset += height * skip

    return particles
