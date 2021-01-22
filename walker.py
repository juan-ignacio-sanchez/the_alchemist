from collections import namedtuple

import pygame
from pygame.math import Vector2

from text.text import show_score
from models import Item, Player, Enemy
from constants import FACING_EAST, FACING_WEST

Size = namedtuple('Size', ['width', 'height'])


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
    screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN, vsync=1)
    sprites_image = pygame.image.load("assets/sprites/sprites.png").convert()
    # SOUND
    bottle_picked = pygame.mixer.Sound("assets/sounds/bottle_picked.ogg")
    player_killed_sound = pygame.mixer.Sound("assets/sounds/kill.ogg")
    background_sound = pygame.mixer.Sound("assets/sounds/background/Guitar-Mayhem-2.mp3")
    background_sound.set_volume(0.07)
    background_sound.play(loops=-1)
    score = 0

    # Player
    player = Player(screen, sprites_image, initial_position=(50, 50))
    player.velocity = Vector2(0, 0)

    # Enemy
    enemy = Enemy(screen, sprites_image,
                  skin='BLOOD_CRYING_MOB', facing=FACING_WEST,
                  initial_position=(screen.get_width(), 0))
    enemy.velocity = Vector2(-.5, .5)

    # Items
    mana = Item(screen, sprites_image)

    player_sprites = pygame.sprite.RenderUpdates(player)
    item_sprites = pygame.sprite.RenderUpdates(mana)
    mobs_sprites = pygame.sprite.RenderUpdates(enemy)
    all_sprites = pygame.sprite.RenderUpdates(player, enemy, mana)

    background = create_background(screen, sprites_image)
    screen.blit(background, (0, 0, display_size.width, display_size.height))
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

        # TODO: remove this line (**)
        screen.blit(background, (0, 0, display_size.width, display_size.height))

        # TODO: convert Score into a Sprite
        score_dirty = show_score(f'Score: {score}', screen)

        # TODO: (**) in favor of clearing sprites
        all_sprites.clear(screen, background)

        all_sprites.update(player_position=player.center_position)

        # COLISSIONS ++++++++
        if player.alive() and pygame.sprite.spritecollide(player, mobs_sprites, dokill=False):
            player.kill()
            player_killed_sound.play()

        if pygame.sprite.spritecollide(player, item_sprites,
                                       dokill=False,
                                       collided=pygame.sprite.collide_rect_ratio(0.7)):
            score += 1
            bottle_picked.play()
            mana.spawn()
        # +++++++++++++++++++

        sprites_dirty = item_sprites.draw(screen)
        sprites_dirty += mobs_sprites.draw(screen)
        sprites_dirty += player_sprites.draw(screen)

        dirty_rects = [score_dirty] + sprites_dirty

        pygame.display.update(dirty_rects)
        # pygame.display.flip()
        main_clock.tick(60)


if __name__ == '__main__':
    main()
