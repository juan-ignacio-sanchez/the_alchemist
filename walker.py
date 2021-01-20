import time
from collections import namedtuple

import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2

from fps.fps import display_fps
from constants import CHARACTERS, CHARACTERS_DICT

Size = namedtuple('Size', ['width', 'height'])

FACING_EAST = 0
FACING_WEST = 1

class Walker(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface):
        super().__init__()
        self.surface = surface

        # Skin related stuff
        self.skin = 'OLD_MAN'
        self.original_image = image
        self.image = image.subsurface(pygame.rect.Rect(CHARACTERS_DICT.get(self.skin)))
        self.image = pygame.transform.scale(self.image, (12 * 5, 17 * 5))
        self.last_skin_change = time.time()
        self.facing = FACING_EAST

        self.rect = self.image.get_rect()
        self.rect.y = surface.get_height() - self.rect.height - 10

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0.1)

    def next_skin(self):
        if time.time() - self.last_skin_change > 1:
            print("skin changed!")
            self.skin = CHARACTERS[(CHARACTERS.index(self.skin) + 1) % len(CHARACTERS)]
            self.image = self.original_image.subsurface(pygame.rect.Rect(CHARACTERS_DICT.get(self.skin)))
            self.image = pygame.transform.scale(self.image, (12 * 5, 17 * 5))
            self.last_skin_change = time.time()

    def move(self):
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position

    def bounce(self):
        if not 0 < self.center_position.x < self.surface.get_width():
            self.velocity.x *= -1

        if not 0 < self.center_position.y < self.surface.get_height():
            self.velocity.y *= -1

    def change_facing(self, key):
        if key == pygame.K_RIGHT and not self.facing == FACING_EAST:
            self.facing = FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif key == pygame.K_LEFT and not self.facing == FACING_WEST:
            self.facing = FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()

    def on_key_pressed(self, key):
        if key == pygame.K_RIGHT:
            self.velocity = self.velocity + Vector2(.5, 0)
        elif key == pygame.K_LEFT:
            self.velocity = self.velocity + Vector2(-.5, 0)
        elif key == pygame.K_UP:
            self.velocity = self.velocity + Vector2(0, -.5)
        elif key == pygame.K_DOWN:
            self.velocity = self.velocity + Vector2(0, .5)
        elif key == pygame.K_s:
            self.next_skin()

        self.change_facing(key)


def create_background(screen: pygame.Surface, image: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(
        image.subsurface(pygame.rect.Rect(0, 91, 64, 48)),
        (screen.get_rect().width, screen.get_rect().height)
    )


def main():
    pygame.init()
    main_clock = pygame.time.Clock()
    run = True
    display_size = Size(width=600, height=480)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE, vsync=1)
    sprites_image = pygame.image.load("sprites.png").convert()
    player = Walker(screen, sprites_image)
    player.velocity = Vector2(3, 7)
    all_sprites = pygame.sprite.RenderUpdates(player)

    background = create_background(screen, sprites_image)
    screen.blit(background, (0, 0))
    pygame.display.flip()
    pygame.key.set_repeat(1, 35)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                player.on_key_pressed(event.key)

        screen.blit(background, (0, 0, display_size.width, display_size.height))
        fps_dirty = display_fps(main_clock, screen)

        all_sprites.update()
        sprites_dirty = all_sprites.draw(screen)

        dirty_rects = [fps_dirty] + sprites_dirty

        pygame.display.update(dirty_rects)
        main_clock.tick(60)


if __name__ == '__main__':
    main()