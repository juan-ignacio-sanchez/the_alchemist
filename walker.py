import random
from collections import namedtuple
from pathlib import Path

import pygame
from pygame.math import Vector2

from models import Item, Player, Enemy, Score
from constants import FACING_WEST

Size = namedtuple('Size', ['width', 'height'])


def create_background(screen: pygame.Surface, image: pygame.Surface) -> pygame.Surface:
    return pygame.transform.scale(
        image.subsurface(pygame.rect.Rect(0, 91, 64, 48)),
        (screen.get_rect().width, screen.get_rect().height)
    )


def select_background_sound():
    sounds = Path('assets/sounds/background')
    return random.choice(list(sounds.iterdir()))


def main():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    main_clock = pygame.time.Clock()
    run = True
    display_size = Size(width=800, height=600)
    screen = pygame.display.set_mode(display_size, pygame.RESIZABLE, vsync=1)
    sprites_image = pygame.image.load("assets/sprites/sprites.png").convert()
    # SOUND
    bottle_picked = pygame.mixer.Sound("assets/sounds/bottle_picked.ogg")
    player_killed_sound = pygame.mixer.Sound("assets/sounds/kill.ogg")
    background_sound = pygame.mixer.Sound(select_background_sound())
    ending_sound = pygame.mixer.Sound("assets/sounds/ending.mp3")
    background_sound.set_volume(0.07)
    ending_sound.set_volume(0.07)
    background_sound.play(loops=-1)
    score = Score(screen)

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
    all_sprites = pygame.sprite.OrderedUpdates(score, mana, enemy, player)

    background = create_background(screen, sprites_image)
    screen.blit(background, (0, 0, display_size.width, display_size.height))
    pygame.display.flip()
    pygame.key.set_repeat(1, 35)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player_sprites.add(player)
                    all_sprites.add(player)
                    score.value = 0
                    player.restore_initial_position()
                    enemy.restore_initial_position()
                    ending_sound.stop()
                    background_sound.stop()
                    background_sound.play()

                player.on_key_pressed(event.key)

        all_sprites.clear(screen, background)

        # COLISSIONS ++++++++
        if player.alive() and pygame.sprite.spritecollide(player, mobs_sprites, dokill=False):
            player.kill()
            player_killed_sound.play()
            background_sound.stop()
            ending_sound.play(loops=-1)
            enemy.velocity.update(0,0)
            enemy.acceleration.update(0.01, 0.01)

        if pygame.sprite.spritecollide(player, item_sprites,
                                       dokill=False,
                                       collided=pygame.sprite.collide_rect_ratio(0.7)):
            score.value += 1
            bottle_picked.play()
            mana.spawn()
        # +++++++++++++++++++

        all_sprites.update(player_position=player.center_position)

        sprites_dirty = all_sprites.draw(screen)

        pygame.display.update(sprites_dirty)
        main_clock.tick(60)


if __name__ == '__main__':
    main()
