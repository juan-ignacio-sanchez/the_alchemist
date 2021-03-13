import os

from pygame import FULLSCREEN, RESIZABLE, SCALED, DOUBLEBUF, HWACCEL, HWSURFACE


VOLUME = 0.1
SFX_VOLUME = 0.3

# NOTE: at some point I should be able to remove the SCALED flag, according to this
#       github thread: https://github.com/pygame/pygame/issues/735
DISPLAY_MODE_FULL = RESIZABLE | SCALED | DOUBLEBUF | HWACCEL | HWSURFACE
DISPLAY_MODE_WIND = RESIZABLE | SCALED

AUDIO_EXTENSION = ".ogg" if os.name == "posix" else ".wav"
