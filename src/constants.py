import settings
from pathlib import Path

SCALE_FACTOR = 6
ITEMS_SCALE_FACTOR = 5
UI_SCALE_FACTOR = 2

# Rendering Layers
LAYER_SCORE = 0
LAYER_ITEM = 1
LAYER_ENEMY = 2
LAYER_PLAYER = 3
LAYER_WEAPON = 4
LAYER_PARTICLE = 5

FACING_EAST = 0
FACING_WEST = 1

PLAYER_RECT_OLD_MAN = (98, 224, 12, 16)
PLAYER_RECT_OLD_MAN_STEP_OUT = (0, 0, 12, 16)
PLAYER_RECT_OLD_MAN_STEP_IN = (13, 0, 12, 16)
PLAYER_WALKING_SEQUENCE = [PLAYER_RECT_OLD_MAN_STEP_OUT, PLAYER_RECT_OLD_MAN_STEP_IN]

PLAYER_OLD_MAN = "OLD_MAN"

PLAYER_DICT = {
    PLAYER_OLD_MAN: PLAYER_RECT_OLD_MAN,
}

MOB_SMALL_BLOOD_CRYING = "SMALL_BLOOD_CRYING_MOB"
MOB_BLOOD_CRYING = "BLOOD_CRYING_MOB"
MOB_ROTTEN_BLOOD_CRYING = "ROTTEN_BLOOD_CRYING_MOB"
MOB_SMALL_TROLL = "SMALL_TROLL_MOB"
MOB_BIG_TROLL = "BIG_TROLL_MOB"
MOB_MASKED_TROLL = "MASKED_TROLL"
MOB_SMALL_DEVIL = "SMALL_DEVIL"
MOB_TALL_DEVIL = "TALL_DEVIL"

MOB_RECT_SMALL_BLOOD_CRYING = (3, 150, 9, 10)
MOB_RECT_BLOOD_CRYING = (36, 144, 8, 16)
MOB_RECT_ROTTEN_BLOOD_CRYING = (52, 144, 8, 16)
MOB_RECT_SMALL_TROLL = (34, 160, 11, 16)
MOB_RECT_BIG_TROLL = (102, 182, 20, 26)
MOB_RECT_MASKED_TROLL = (18, 161, 12, 15)
MOB_RECT_SMALL_DEVIL = (3, 180, 10, 12)
MOB_RECT_TALL_DEVIL = (3, 180, 10, 16)


MOBS_DICT = {
    MOB_SMALL_BLOOD_CRYING: MOB_RECT_SMALL_BLOOD_CRYING,
    MOB_BLOOD_CRYING: MOB_RECT_BLOOD_CRYING,
    MOB_ROTTEN_BLOOD_CRYING: MOB_RECT_ROTTEN_BLOOD_CRYING,
    MOB_SMALL_TROLL: MOB_RECT_SMALL_TROLL,
    MOB_BIG_TROLL: MOB_RECT_BIG_TROLL,
    MOB_MASKED_TROLL: MOB_RECT_MASKED_TROLL,
    MOB_SMALL_DEVIL: MOB_RECT_SMALL_DEVIL,
    MOB_TALL_DEVIL: MOB_RECT_TALL_DEVIL,
}

MOBS = ["BLOOD_CRYING_MOB"]

GREEN_LIQUID_ITEM = (133, 212, 7, 11)
WIDE_GREEN_LIQUID_ITEM = (196, 196, 9, 11)
WIDE_RED_LIQUID_ITEM = (196, 180, 9, 11)
WIDE_BLUE_LIQUID_ITEM = (196, 212, 9, 11)

POTION_RED = 0
POTION_GREEN = 1
POTION_BLUE = 2
POTION_COLORS = {
    POTION_RED: WIDE_RED_LIQUID_ITEM,
    POTION_BLUE: WIDE_BLUE_LIQUID_ITEM,
    POTION_GREEN: WIDE_GREEN_LIQUID_ITEM,
}


# Weapons
BASIC_SWORD = (179, 10, 10, 21)

# Backgrounds
FLOOR_BACKGROUND = (0, 91, 64, 48)
WALL_BACKGROUND = (1, 12, 46, 25)
WALL_FRONT_BACKGROUND = (1, 12, 46, 7)
BACKGROUND_COLUMN = (208, 181, 16, 33)

# UI
# Corners
UI_BOX_CORNER_TOP_LEFT = (64, 41, 6, 7)
UI_BOX_CORNER_BOTTOM_LEFT = (64, 56, 8, 7)
UI_BOX_CORNER_BOTTOM_RIGHT = (96, 56, 8, 7)
UI_BOX_CORNER_TOP_RIGHT = (98, 41, 6, 7)
# Horizontal bars
UI_BOX_TOP_HORIZONTAL_BAR = (71, 41, 1, 6)
UI_BOX_BOTTOM_HORIZONTAL_BAR = (74, 58, 1, 5)
# Vertical bars
UI_BOX_VERTICAL_BAR_LEFT = (64, 48, 6, 1)
UI_BOX_VERTICAL_BAR_RIGHT = (98, 48, 6, 1)
# Background
UI_BOX_BACKGROUND = (80, 104, 24, 24)
UI_BOX_BACKGROUND_COLOR_PAPYRUS = (211, 191, 169)
UI_BOX_TEXT_COLOR_PAPYRUS = (71, 58, 57)

# Fonts
FONTS_BASE_PATH = Path(__file__).parent / "assets/fonts"
FONT_PATH_PAUSED = FONTS_BASE_PATH / "young_serif_regular.otf"
FONT_PATH_HELPER = FONTS_BASE_PATH / "young_serif_regular.otf"
FONT_PATH_MAIN = FONTS_BASE_PATH / "young_serif_regular.otf"
FONT_PATH_SECONDARY = FONTS_BASE_PATH / "young_serif_regular.otf"

# Sprites
SPRITES_BASE_PATH = Path(__file__).parent / "assets/sprites"
SPRITES_PATH = SPRITES_BASE_PATH / "sprites.png"
SPRITES_UI_PATH = SPRITES_BASE_PATH / "sprites_ui.png"
SPRITES_PLAYER_WALKING = SPRITES_BASE_PATH / "old_man_walking.png"

# Sound

SOUNDS_BASE_PATH = Path(__file__).parent / "assets/sounds"
BACKGROUND_SOUND = (
    SOUNDS_BASE_PATH / f"background/Guitar-Mayhem-6{settings.AUDIO_EXTENSION}"
)
ENDING_SOUND = SOUNDS_BASE_PATH / f"ending{settings.AUDIO_EXTENSION}"
MAIN_MENU_SOUND = SOUNDS_BASE_PATH / f"main_menu{settings.AUDIO_EXTENSION}"

# SFX
SFX_BASE_PATH = SOUNDS_BASE_PATH / "sfx"
SFX_BOTTLE_PICKED = SFX_BASE_PATH / "bottle_picked.wav"
SFX_PLAYER_KILLED = SFX_BASE_PATH / "kill.wav"
SFX_WALL_HIT = SFX_BASE_PATH / "boundary_hit.wav"
SFX_MENU_ITEM_CHANGED = SFX_BASE_PATH / "menu_item_changed.wav"
SFX_ENEMY_KILLED = SFX_BASE_PATH / "banishing.wav"
SFX_PLAYER_WIN = SFX_BASE_PATH / "win_sound.wav"
SFX_INTERLUDE_WIN = SFX_BASE_PATH / "interlude_win_sound.wav"
SFX_FOOTSTEPS = SFX_BASE_PATH / "footsteps.mp3"
SFX_SWORD_BRANDISHING = SFX_BASE_PATH / "sword_brandishing.wav"

# Texts
TEXTS_BASE_PATH = Path(__file__).parent / "assets/text"
TEXT_CREDITS_PATH = TEXTS_BASE_PATH / "credits.txt"
TEXT_CONTROLS_PATH = TEXTS_BASE_PATH / "controls.txt"
