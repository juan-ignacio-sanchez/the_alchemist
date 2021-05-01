import os

import pygame as pg
from pygame import FULLSCREEN, RESIZABLE, SCALED, DOUBLEBUF, HWACCEL, HWSURFACE

LOG_LEVEL = os.getenv('LOG_LEVEL', default='WARNING')

GENERAL_VOLUME = 1
VOLUME = 0 * GENERAL_VOLUME
SFX_VOLUME = 0.3 * GENERAL_VOLUME

# NOTE: at some point I should be able to remove the SCALED flag, according to this
#       github thread: https://github.com/pygame/pygame/issues/735
DISPLAY_MODE_FULL = FULLSCREEN | SCALED | DOUBLEBUF | HWACCEL | HWSURFACE
DISPLAY_MODE_WIND = RESIZABLE | SCALED

AUDIO_EXTENSION = ".ogg" if os.name == "posix" else ".wav"

KEY_UP = pg.K_UP
KEY_DOWN = pg.K_DOWN
KEY_LEFT = pg.K_LEFT
KEY_RIGHT = pg.K_RIGHT
