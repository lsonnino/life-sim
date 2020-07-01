import pygame
import numpy as np
from itertools import compress

from src.constants import WATER_COLOR, DIRT_COLOR, GRASS_COLOR, HUMAN_COLOR
from src.constants import SIZE, WIDTH, HEIGHT, WATER_LEVEL
from src.constants import INITIAL_POPULATION, reproduction_distance
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

    def __build_adjacent_matrix(self):
        size = len(self.population)
        matrix = np.zeros((size, size))
        closest = np.zeros((size, 4)) - 1

        for i in range(size):
            for j in range(i + 1, size):
                dx = self.population[i].x - self.population[j].x
                dy = self.population[i].y - self.population[j].y

                matrix[i, j] = dx + dy
                matrix[j, i] = matrix[i, j]

                if dx < 0:  # j is to the west
                    ci = closest[i][1]
                    cj = closest[j][0]
                    closest[i][1] = min(-dx, ci) if ci >= 0 else -dx
                    closest[j][0] = -dx if cj >= 0 else -dx
                elif dx > 0:  # j is to the east
                    ci = closest[i][0]
                    cj = closest[j][1]
                    closest[i][0] = min(dx, ci) if ci >= 0 else dx
                    closest[j][1] = dx if cj >= 0 else dx
                else:  # j is on the same coordinate
                    closest[i][0] = closest[i][1] = closest[j][0] = closest[j][1] = 0

                if dy < 0:  # j is to the south
                    ci = closest[i][3]
                    cj = closest[j][2]
                    closest[i][3] = min(-dy, ci) if ci >= 0 else -dy
                    closest[j][2] = -dy if cj >= 0 else -dy
                elif dy > 0:  # j is to the north
                    ci = closest[i][2]
                    cj = closest[j][3]
                    closest[i][2] = min(dy, ci) if ci >= 0 else dy
                    closest[j][3] = dy if cj >= 0 else dy
                else:  # j is on the same coordinate
                    closest[i][2] = closest[i][3] = closest[j][2] = closest[j][3] = 0

        return np.array(matrix), np.array(closest), size

    def tick(self, map):
        matrix, closest, size = self.__build_adjacent_matrix()
        to_remove = [False] * size

        for i in range(size):
            h = self.population[i]

            h.tick()

            map_level = [
                map[h.x - 1, h.y] if 0 <= h.x - 1 else 0,
                map[h.x + 1, h.y] if h.x + 1 < WIDTH else 0,
                map[h.x, h.y - 1] if 0 <= h.y - 1 else 0,
                map[h.x, h.y + 1] if h.y + 1 < HEIGHT else 0
            ]
            population_density = len(np.where(matrix[i] <= 1)) / size

            h.move(map_level, closest[i], population_density)

            to_remove[i] = h.is_alive(map, population_density)

        self.population = list(compress(self.population, to_remove))

        size = len(self.population)
        # todo

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

    def tick(self):
        self.population_handler.tick(self.map)

    def draw(self):
        # Draw the map
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.__draw_case(case_color(self.map[x, y]), x, y)

        # Draw population
        self.population_handler.draw(self.window)
