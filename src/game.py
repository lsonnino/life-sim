import pygame
import numpy as np
from itertools import compress
import random
import pickle

from src.constants import WATER_COLOR, DIRT_COLOR, GRASS_COLOR, HUMAN_COLOR
from src.constants import SIZE, WIDTH, HEIGHT, WATER_LEVEL
from src.constants import INITIAL_POPULATION, reproduction_distance, reproduction_rest, population_distance,\
    mutation_rate, aging
from src.constants import DATA_DIRECTORY, LOAD
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
        self.reproduction_wait = 0
        self.gen = 0
        self.gen_advance = 0.0
        self.flags = [True, True, True, True]

        if LOAD >= 0:
            self.__load()

    def __load(self):
        with open(DATA_DIRECTORY + '/' + str(LOAD) + '.data', 'rb') as f:
            self.population = pickle.load(f)
            self.gen = LOAD
            self.__set_flags()

            print("Loaded generation", self.gen)

    def __save(self):
        with open(DATA_DIRECTORY + '/' + str(self.gen) + '.data', 'wb') as f:
            pickle.dump(self.population, f)

    def __set_flags(self):
        flag_mod = int(self.gen / 10)
        for i in range(flag_mod):
            if self.flags[i]:
                self.flags[i] = False
                print("Set to false flag", flag_mod)

    def __build_adjacent_matrix(self, do_closest=True):
        size = len(self.population)
        matrix = np.zeros((size, size))
        closest = np.zeros((size, 4)) - 1

        for i in range(size):
            for j in range(i + 1, size):
                dx = self.population[i].x - self.population[j].x
                dy = self.population[i].y - self.population[j].y

                matrix[i, j] = dx + dy
                matrix[j, i] = matrix[i, j]

                if not do_closest:
                    continue

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

    def __reproduce(self):
        matrix, _, size = self.__build_adjacent_matrix(do_closest=False)
        to_add = []
        for i in range(size):
            for j in range(i + 1, size):
                if matrix[i, j] <= reproduction_distance and \
                        self.population[i].want_reproduce(self.population[j]) and \
                        self.population[j].want_reproduce(self.population[i]):
                    to_add.append(self.population[i].reproduce(self.population[j]))
        self.population = self.population + to_add

    def __population_injection(self):
        size = len(self.population) - 1  # -1 to ensure to avoid array index out of bound
        for i in range(INITIAL_POPULATION):
            female = self.population[int(random.random() * size)]
            male = self.population[int(random.random() * size)]

            self.population.append(female.reproduce(
                male,
                mutation_rate=max(0.95 ** self.gen, mutation_rate)
            ))

    def tick(self, map):
        matrix, closest, size = self.__build_adjacent_matrix()
        to_remove = [False] * size

        # Move
        for i in range(size):
            h = self.population[i]

            h.tick()

            map_level = [
                map[h.x - 1, h.y] if 0 <= h.x - 1 else 0,
                map[h.x + 1, h.y] if h.x + 1 < WIDTH else 0,
                map[h.x, h.y - 1] if 0 <= h.y - 1 else 0,
                map[h.x, h.y + 1] if h.y + 1 < HEIGHT else 0
            ]
            population_density = len(np.where(matrix[i] <= population_distance)) / size
            c_east = closest[i][0] / WIDTH
            c_west = closest[i][1] / WIDTH
            c_north = closest[i][2] / HEIGHT
            c_south = closest[i][3] / HEIGHT
            c_east = c_east if c_east >= 0 else 1
            c_west = c_west if c_west >= 0 else 1
            c_north = c_north if c_north >= 0 else 1
            c_south = c_south if c_south >= 0 else 1

            h.move(map_level, [c_east, c_west, c_north, c_south], population_density)

            to_remove[i] = h.is_alive(map, population_density, self.flags)

        # Remove those who are dead
        next_gen = list(compress(self.population, to_remove))

        # Slow start
        if len(next_gen) <= 2:
            self.__population_injection()
            self.reproduction_wait = 0  # disable reproduction
            self.gen += 1
            self.gen_advance = 0.0

            print("Forced reproduction for generation", self.gen)
            self.__save()
        else:
            self.population = next_gen

        # Set the difficulty for next generation
        self.__set_flags()

        # Reproduce
        if (not self.flags[-1]) and self.reproduction_wait == reproduction_rest:
            self.reproduction_wait = 0
            self.__reproduce()
        self.reproduction_wait += 1

        # Next generation
        if self.gen_advance >= 1:
            self.gen_advance = 0.0
            self.gen += 1
            print("Generation", self.gen)

        self.gen_advance += aging

    def draw(self, window):
        for h in self.population:
            pygame.draw.circle(window, HUMAN_COLOR, (h.x * SIZE, h.y * SIZE), SIZE / 2)


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
