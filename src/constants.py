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
DIRT_COLOR = (155, 118, 83)
GRASS_COLOR = (99, 201, 0)


###############################
#   GAME CONSTANTS
###############################

SIZE = 10
WIDTH = floor(WIN_SIZE[0] / SIZE)
HEIGHT = floor(WIN_SIZE[1] / SIZE)

NOISE_DECAY = 0.8
# SEED = 7839261739
SEED = 8629378618930
WATER_LEVEL = 0.5
