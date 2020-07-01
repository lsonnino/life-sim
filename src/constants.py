from math import floor

###############################
#   GENERAL PARAMETERS
###############################

# SEED = 7839261739
SEED = 8629378618930

INITIAL_POPULATION = 100

###############################
#   GAME MECANICS
###############################

water_decrease = 0.01
food_decrease = 0.05
aging = 0.001

drowning = 0.01
disease_rate = 0.9
population_distance = 1

reproduction_rate = 0.01
reproduction_distance = 0
mutation_rate = 0.01

###############################
#   PYGAME PARAMETERS
###############################

NAME = 'Life Sim'
VERSION = '1.0'
WIN_SIZE = (1280, 720)
FPS = 25


###############################
#   COLORS
###############################

BACKGROUND_COLOR = (0, 0, 0)

WATER_COLOR = (54, 141, 197)
DIRT_COLOR = (155, 118, 83)
GRASS_COLOR = (110, 180, 50)

HUMAN_COLOR = (141, 85, 36)


###############################
#   GAME CONSTANTS
###############################

SIZE = 10
WIDTH = floor(WIN_SIZE[0] / SIZE)
HEIGHT = floor(WIN_SIZE[1] / SIZE)

NOISE_DECAY = 0.8
WATER_LEVEL = 0.5

###############################
#   AGENT CONSTANTS
###############################
NOTHING = 0
EAST = 1
WEST = 2
NORTH = 3
SOUTH = 4

YES = 0
NO = 1
