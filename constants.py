import settings

SCALE_FACTOR = 6
ITEMS_SCALE_FACTOR = 4

FACING_EAST = 0
FACING_WEST = 1

OLD_MAN = (98, 224, 12, 16)
PIRATE = (113, 224, 14, 16)
RED_WIZARD = (128, 224, 15, 16)
PURPLE_WIZARD = (144, 224, 15, 16)

CHARACTERS_DICT = {
    'OLD_MAN': OLD_MAN,
    'PIRATE': PIRATE,
    'RED_WIZARD': RED_WIZARD,
    'PURPLE_WIZARD': PURPLE_WIZARD,
}

CHARACTERS = [
    'OLD_MAN',
    'PIRATE',
    'RED_WIZARD',
    'PURPLE_WIZARD',
]

BLOOD_CRYING_MOB = (36, 144, 8, 16)

MOBS_DICT = {
    'BLOOD_CRYING_MOB': BLOOD_CRYING_MOB,
}

MOBS = [
    'BLOOD_CRYING_MOB'
]

GREEN_LIQUID_ITEM = (133, 212, 7, 11)
WIDE_GREEN_LIQUID_ITEM = (196, 196, 9, 11)
WIDE_RED_LIQUID_ITEM = (196, 180, 9, 11)
WIDE_BLUE_LIQUID_ITEM = (196, 212, 9, 11)

# Weapons
BASIC_SWORD = (179, 10, 10, 21)

# Sound
BACKGROUND_SOUND = "./assets/sounds/background/Guitar-Mayhem-6" + settings.AUDIO_EXTENSION
ENDING_SOUND = "assets/sounds/ending" + settings.AUDIO_EXTENSION
MAIN_MENU_SOUND = "assets/sounds/main_menu" + settings.AUDIO_EXTENSION

# SFX
BOTTLE_PICKED_SFX = "assets/sounds/sfx/bottle_picked.wav"
PLAYER_KILLED_SFX = "assets/sounds/sfx/kill.wav"
WALL_HIT_SFX = "assets/sounds/sfx/boundary_hit.wav"
MENU_ITEM_CHANGED_SFX = "./assets/sounds/sfx/menu_item_changed.wav"
