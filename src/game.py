import numpy as np
import random
# import pygame

from src.constants import BACKGROUND_COLOR, WATER_COLOR, LAND_MAX_COLOR
from src.constants import SIZE, WIDTH, HEIGHT, SEED, WATER_LEVEL


def case_color(value):
    if value < WATER_LEVEL:
        return WATER_COLOR
    else:
        return LAND_MAX_COLOR


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

                map[x, y] = random.random() * 2 - 1 + x1 + y1

    return map


class Game(object):
    def __init__(self, window):
        self.window = window
        self.map = generate_map()

        map_max = np.amax(self.map)
        map_min = np.amin(self.map)
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if self.map[x, y] > 0:
                    self.map[x, y] = self.map[x, y] / abs(map_max)
                else:
                    self.map[x, y] = self.map[x, y] / abs(map_min)

    def __draw_case(self, color, x, y):
        self.window.fill(color, (SIZE * x, SIZE * y, SIZE, SIZE))

    def draw(self):
        # Draw the map
        for x in range(WIDTH):
            for y in range(HEIGHT):
                self.__draw_case(case_color(self.map[x, y]), x, y)
