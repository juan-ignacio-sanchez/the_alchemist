from random import choice

import pygame

import constants
from sprites.ui import Score, EphemeralBanner


class Level:
    def __init__(self, screen, display_size, max_score,
                 title=None, allowed_enemies=None, allowed_potions=None):
        self.number = 0
        self.title = title or "No title"
        self.screen = screen
        self.score = Score(self.screen, max_score=max_score, seconds_to_leave=4)
        self.allowed_enemies = allowed_enemies or [
            constants.MOB_BIG_TROLL,
        ]
        self.allowed_potions = allowed_potions or [
            constants.POTION_GREEN,
            constants.POTION_RED,
            constants.POTION_BLUE,
        ]
        self._announce_win_flag = True
        self.next_level = None

    def random_enemy(self):
        return choice(self.allowed_enemies)

    def random_potion(self):
        return choice(self.allowed_potions)

    def announce_win(self):
        flag = self._announce_win_flag
        self._announce_win_flag = False
        return flag

    def put_banner(self, group: pygame.sprite.Group):
        group.add(EphemeralBanner(2, self.screen, main_text=self.title,
                                  secondary_text=f'Level {self.number}'))


def load_levels(screen):
    levels = [
        Level(screen, screen.get_size(), max_score=3, title='Apprentice',
              allowed_enemies=[
                  constants.MOB_SMALL_BLOOD_CRYING,
              ],
              allowed_potions=[
                  constants.POTION_GREEN,
              ]),
        Level(screen, screen.get_size(), max_score=3, title='Blacksmith',
              allowed_enemies=[
                  constants.MOB_SMALL_BLOOD_CRYING,
                  constants.MOB_BLOOD_CRYING,
              ],
              allowed_potions=[
                  constants.POTION_BLUE,
              ]),
        Level(screen, screen.get_size(), max_score=3, title='Cursed',
              allowed_enemies=[
                  constants.MOB_SMALL_BLOOD_CRYING,
                  constants.MOB_BLOOD_CRYING,
                  constants.MOB_SMALL_TROLL,
              ],
              allowed_potions=[
                  constants.POTION_RED,
              ]),
        Level(screen, screen.get_size(), max_score=10, title="There's hope",
              allowed_potions=[
                  constants.POTION_GREEN,
                  constants.POTION_RED,
                  constants.POTION_BLUE,
              ]),
        Level(screen, screen.get_size(), max_score=10, title="Nightmare",
              allowed_enemies=[
                  constants.MOB_BIG_TROLL
              ],
              allowed_potions=[
                  constants.POTION_GREEN,
                  constants.POTION_RED,
                  constants.POTION_BLUE,
              ]),
        Level(screen, screen.get_size(), max_score=15, title="Ouroboros",
              allowed_enemies=[
                  constants.MOB_BIG_TROLL,
                  constants.MOB_MASKED_TROLL,
                  constants.MOB_SMALL_TROLL,
              ],
              allowed_potions=[
                  constants.POTION_GREEN,
                  constants.POTION_RED,
              ]),
        Level(screen, screen.get_size(), max_score=25, title="Rotten Wood",
              allowed_enemies=[
                  constants.MOB_ROTTEN_BLOOD_CRYING
              ],
              allowed_potions=[
                  constants.POTION_GREEN,
                  constants.POTION_RED,
              ]),
        Level(screen, screen.get_size(), max_score=30, title="Beyond your sight",
              allowed_enemies=[
                  constants.MOB_SMALL_DEVIL,
                  constants.MOB_TALL_DEVIL
              ],
              allowed_potions=[
                  constants.POTION_GREEN,
                  constants.POTION_RED,
                  constants.POTION_BLUE,
              ]),
        Level(screen, screen.get_size(), max_score=30, title="This is Hell",
              allowed_potions=[
                  constants.POTION_RED,
              ]),
    ]
    for i in range(len(levels)-1):
        levels[i].next_level = levels[i+1]

    levels_total = len(levels)
    for i in range(levels_total):
        levels[i].number = i + 1

    return levels[0]
