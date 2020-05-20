# *-* coding: utf8 *-*

# Defines main game constants that can be used everywhere

# Main internal constants
import math
PI = math.pi
DEF_PI_DIVIDE = 160
DEF_ANGLE = (PI / DEF_PI_DIVIDE)

# camera modes
CAMERA_TOP = 1
CAMERA_SUBJECTIVE = 2

# global configuration
CONFIG_RESOURCE_DIR = "res"
CONFIG_DATA_DIR = "data"
INTERVAL_TICK_RESOLUTION = 0.01

# Audio constants
AUDIO_FX_VOLUME = 0.8
AUDIO_FX_SIGNAL_VOLUME = (AUDIO_FX_VOLUME / 1.5)
AUDIO_MUSIC_VOLUME = 0.8
AUDIO_FADE_INTERVAL = 10
AUDIO_STEREO_FIELD_WIDTH = 95
AUDIO_ERROR_SOUND = "error-sound"
AUDIO_MESSAGE_SOUND = "message"
AUDIO_MESSAGE_FINISH_SOUND = "messageFinished"

AUDIO_FOOTSTEP_WALK_SOUND = "walk"
AUDIO_FOOTSTEP_RUN_SOUND = "run"

# Scene constants

SCENE_MININUM_INTERVAL = 10 # milliseconds
# directions the player can go to

DIRECTION_NORTH = 0
DIRECTION_SOUTH = 1
DIRECTION_EAST = 2
DIRECTION_WEST = 3


# Objects specific constants
HERO_WALK_TIME = 500
HERO_RUN_TIME = 300
OBJECT_ECHO_TIME = 1000
OBJECT_MAX_DISTANCE = 10
CHARACTER_STAMINA_RECOVERY_TIME = 50
# Peckables
LOCKSTATE_LOCKED = 100
LOCKSTATE_UNLOCKED = 101
