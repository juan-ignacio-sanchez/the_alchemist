from collections import namedtuple

import pygame
from pygame.sprite import Sprite

from fps.fps import display_fps

Size = namedtuple('Size', ['width', 'height'])

STATE_ASCENDING = 0
STATE_DESCENDING = 1
STATE_STANDING = 2


class Walker(Sprite):
    def __init__(self, surface: pygame.Surface):
        super().__init__()
        self.surface = surface
        self.image = pygame.Surface((50, 100))
        self.image.fill('red')

        self.rect = self.image.get_rect()
        self.rect.y = surface.get_height() - self.rect.height - 10

        self.current_state = STATE_STANDING
        self.jumping = False

    def update(self, *args, **kwargs) -> None:
        if self.current_state == STATE_ASCENDING:
            if self.rect.y + self.rect.height > self.surface.get_height() - 20:
                self.rect.y -= 1
            else:
                self.current_state = STATE_DESCENDING
        elif self.current_state == STATE_DESCENDING:
            self.rect.y += 1
            if self.rect.y + self.rect.height >= self.surface.get_height():
                self.rect.y = self.surface.get_height() - self.rect.height
                self.current_state = STATE_STANDING

    def on_key_pressed(self, key):
        if key == pygame.K_RIGHT:
            self.rect = self.rect.move(10, 0)
        elif key == pygame.K_LEFT:
            self.rect = self.rect.move(-10, 0)
        elif key == pygame.K_SPACE:
            self.current_state = STATE_ASCENDING

def main():
    pygame.init()
    main_clock = pygame.time.Clock()
    run = True
    display_size = Size(width=600, height=480)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE)
    player = Walker(screen)
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