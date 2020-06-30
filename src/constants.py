from math import floor

###############################
#   PYGAME PARAMETERS
###############################

NAME = 'Life Sim'
VERSION = '1.0'
WIN_SIZE = (1280, 720)
FPS = 1


###############################
#   COLORS
###############################
BACKGROUND_COLOR = (0, 0, 0)
WATER_COLOR = (54, 141, 197)
LAND_MAX_COLOR = (187, 115, 85)


###############################
#   GAME CONSTANTS
###############################

SIZE = 10
WIDTH = floor(WIN_SIZE[0] / SIZE)
HEIGHT = floor(WIN_SIZE[1] / SIZE)

SEED = 7839261739
WATER_LEVEL = 0.0
