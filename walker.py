import time
import random
from collections import namedtuple

import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2

from fps.fps import display_fps
from constants import CHARACTERS, CHARACTERS_DICT, MOBS_DICT

Size = namedtuple('Size', ['width', 'height'])

FACING_EAST = 0
FACING_WEST = 1


class Walker(Sprite):
    def __init__(self, surface: pygame.Surface, image: pygame.Surface, skin='OLD_MAN', facing=FACING_EAST):
        super().__init__()
        self.surface = surface

        # Skin related stuff
        self.skin = skin
        self.original_image = image
        self.set_skin()
        self.last_skin_change = time.time()
        self.facing = facing

        self.rect = self.image.get_rect()
        self.rect.y = surface.get_height() - self.rect.height - 10

        self.center_position = Vector2(self.rect.center)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Sound
        self.knock = pygame.mixer.Sound("knock.mp3")

    def set_skin(self):
        pass

    def apply_force(self, force: Vector2):
        self.acceleration += force

    def move(self):
        self.apply_force(Vector2(0, .3))
        self.velocity += self.acceleration
        self.center_position += self.velocity
        self.rect.center = self.center_position
        self.acceleration *= 0

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
        self.acceleration.update(
            random.random() / 5.0,
            -1 ** random.randrange(0, 1) * random.random() / 10.0,
        )
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

    def next_skin(self):
        if time.time() - self.last_skin_change > 1:
            print("skin changed!")
            self.skin = CHARACTERS[(CHARACTERS.index(self.skin) + 1) % len(CHARACTERS)]
            self.set_skin()
            self.last_skin_change = time.time()

    def change_facing(self, key):
        if key == pygame.K_RIGHT and not self.facing == FACING_EAST:
            self.facing = FACING_EAST
            self.image = pygame.transform.flip(self.image, True, False)
        elif key == pygame.K_LEFT and not self.facing == FACING_WEST:
            self.facing = FACING_WEST
            self.image = pygame.transform.flip(self.image, True, False)

    def on_key_released(self, key):
        if key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN]:
            self.acceleration = Vector2(0, 0)

    def on_key_pressed(self, key):
        if key == pygame.K_RIGHT:
            self.apply_force(Vector2(1, 0))
        elif key == pygame.K_LEFT:
            self.apply_force(Vector2(-1, 0))
        elif key == pygame.K_UP:
            self.apply_force(Vector2(0, -1))
        elif key == pygame.K_DOWN:
            self.apply_force(Vector2(0, 1))
        elif key == pygame.K_s:
            self.next_skin()

        self.change_facing(key)

    def update(self, *args, **kwargs) -> None:
        self.move()
        self.bounce()


def create_background(screen: pygame.Surface, image: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(
        image.subsurface(pygame.rect.Rect(0, 91, 64, 48)),
        (screen.get_rect().width, screen.get_rect().height)
    )


def main():
    pygame.init()
    pygame.mixer.init()
    main_clock = pygame.time.Clock()
    run = True
    display_size = Size(width=800, height=600)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE, vsync=1)
    sprites_image = pygame.image.load("sprites.png").convert()
    player = Player(screen, sprites_image)
    player.velocity = Vector2(3, 7)
    # Enemy
    enemy = Enemy(screen, sprites_image, skin='BLOOD_CRYING_MOB', facing=FACING_WEST)
    enemy.velocity = Vector2(4, 8)
    all_sprites = pygame.sprite.RenderUpdates(player, enemy)

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
            elif event.type == pygame.KEYUP:
                player.on_key_released(event.key)

        screen.blit(background, (0, 0, display_size.width, display_size.height))
        fps_dirty = display_fps(main_clock, screen)

        all_sprites.update()
        sprites_dirty = all_sprites.draw(screen)

        dirty_rects = [fps_dirty] + sprites_dirty

        pygame.display.update(dirty_rects)
        main_clock.tick(60)


if __name__ == '__main__':
    main()