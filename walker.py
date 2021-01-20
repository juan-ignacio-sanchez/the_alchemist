from collections import namedtuple

import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2

from fps.fps import display_fps

Size = namedtuple('Size', ['width', 'height'])


class Walker(Sprite):
    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.image = pygame.Surface((50, 100))
        self.image.fill('red')

        self.rect = self.image.get_rect()
        self.rect.y = surface.get_height() - self.rect.height - 10

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)

    def move(self):
        self.center_position += self.velocity
        self.rect.center = self.center_position

    def bounce(self):
        if not 0 < self.center_position.x < self.surface.get_width():
            self.velocity.x *= -1

        if not 0 < self.center_position.y < self.surface.get_height():
            self.velocity.y *= -1

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()

    def on_key_pressed(self, key):
        if key == pygame.K_RIGHT:
            self.velocity = Vector2(10, 0)
        elif key == pygame.K_LEFT:
            self.velocity = Vector2(-10, 0)
        elif key == pygame.K_UP:
            self.velocity = Vector2(0, -10)
        elif key == pygame.K_DOWN:
            self.velocity = Vector2(0, 10)


def main():
    pygame.init()
    main_clock = pygame.time.Clock()
    run = True
    display_size = Size(width=600, height=480)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE)
    player = Walker(screen)
    player.velocity = Vector2(3, 7)
    all_sprites = pygame.sprite.RenderUpdates(player)

    screen.fill('black')
    pygame.display.flip()
    pygame.key.set_repeat(1, 35)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                player.on_key_pressed(event.key)

        screen.fill('black')
        fps_dirty = display_fps(main_clock, screen)

        all_sprites.update()
        sprites_dirty = all_sprites.draw(screen)

        dirty_rects = [fps_dirty] + sprites_dirty

        pygame.display.update(dirty_rects)
        # pygame.display.flip()
        main_clock.tick(60)


if __name__ == '__main__':
    main()