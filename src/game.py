import pygame

from src.constants import WATER_COLOR, DIRT_COLOR, GRASS_COLOR, HUMAN_COLOR
from src.constants import SIZE, WIDTH, HEIGHT, WATER_LEVEL
from src.constants import INITIAL_POPULATION
from src.map_generator import generate
from src.agent import Human


def case_color(value):
    if value <= WATER_LEVEL:
        return WATER_COLOR
    else:
        dirt_r, dirt_g, dirt_b = DIRT_COLOR
        grass_r, grass_g, grass_b = GRASS_COLOR

        coef = (value - 1) / (WATER_LEVEL - 1)
        co_coef = 1 - coef

        return coef * grass_r + co_coef * dirt_r,\
               coef * grass_g + co_coef * dirt_g,\
               coef * grass_b + co_coef * dirt_b



"""
def generate_map():
    random.seed(SEED)
    map = np.zeros((WIDTH, HEIGHT))

    map[0, 0] = random.random() * 2 - 1
    for total in range(WIDTH + HEIGHT):
        for x in range(total):
            y = total - x

            if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                x1 = map[x - 1, y] if x >= 1 else 0
                y1 = map[x, y - 1] if y >= 1 else 0

                map[x, y] = random.random() * 2 - 1 + (x1 + y1) * MAP_FLATNESS

    return map
"""


class PopulationHandler(object):
    def __init__(self):
        self.population = [Human() for i in range(INITIAL_POPULATION)]

    def draw(self, window):
        for h in self.population:
            pygame.draw.circle(window, HUMAN_COLOR, (h.x * SIZE, h.y * SIZE), SIZE)


class Game(object):
    def __init__(self, window):
        self.window = window
        self.map = generate()
        self.population_handler = PopulationHandler()

    def __draw_case(self, color, x, y):
        self.window.fill(color, (SIZE * x, SIZE * y, SIZE, SIZE))

    def draw(self):
        # Draw the map
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.__draw_case(case_color(self.map[x, y]), x, y)

        # Draw population
        self.population_handler.draw(self.window)
