import numpy as np
import random

from src.constants import WIDTH, HEIGHT, WATER_LEVEL
from src.constants import NOTHING, EAST, WEST, NORTH, SOUTH, YES, NO
from src.constants import water_decrease, food_decrease, aging, disease_rate, drowning, mutation_rate


class NeuralNetwork(object):
    def __init__(self, input, output, hidden=None):
        if hidden is None:
            hidden = []

        self.input = input
        self.output = output
        self.hidden = hidden

        self.weights = []
        self.biases = []

        prev = self.input
        for n in self.hidden:
            self.weights.append(np.zeros((n, prev)).tolist())
            self.biases.append(np.zeros(n).tolist())

            prev = n

        self.weights.append(np.zeros((self.output, prev)).tolist())
        self.biases.append(np.zeros(self.output).tolist())

        self.initialize()

    def initialize(self):
        self.mutate(mutation_rate=1)

    def mutate(self, mutation_rate):
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                for k in range(len(self.weights[i][j])):
                    self.weights[i][j][k] += (2 * random.random() - 1) * mutation_rate

                self.biases[i][j] += (2 * random.random() - 1) * mutation_rate

    def reproduce(self, partner_brain):
        new = NeuralNetwork(self.input, self.output, self.hidden)

        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                for k in range(len(self.weights[i][j])):
                    new.weights[i][j][k] = (self.weights[i][j][k] + partner_brain.weights[i][j][k]) / 2

        for i in range(len(self.biases)):
            for j in range(len(self.biases[i])):
                new.biases[i][j] = (self.biases[i][j] + partner_brain.biases[i][j]) / 2

        return new

    def forward(self, input):
        last_output = input
        current_output = None

        for i in range(len(self.biases)):
            current_output = np.zeros(len(self.biases[i]))

            for j in range(len(current_output)):
                current_output[j] = np.dot(last_output, self.weights[i][j]) + self.biases[i][j]

            last_output = current_output

        return current_output


class Human(object):
    """
    The human has three levels to handle:
        water level (higher is better):
            decreases over time
            need to be close to water to refill
        food level (higher is better)
            decreases over time
            need to be close to enough poeple to refill
        age (lower is better)
            increases over time
            dies when reaches 1

    Reproduction:
        reproduction is triggered whenever he is close enough to someone else
        if both says 'yes', the the two reproduce

    Could die by:
        random death based on age (certain death if age is 1)
        food level reaches 0
        water level reaches 0
        by drowning if goes into too deap waters
        disease because close to too many people for too long

    Thinking:
        This happen on multiple level brain. When a higher priority brain decides to do nothing, the next brain
        chooses the action.

    Survival Brain:
        This brain handles the basic survival instinct of the human
        Priority: 3
        input: 4
            map level left, map level right, map level up, map level down
        output: 5
            do nothing, go east, go west, go north, go south

    Needs Brain:
        This brain handles the needs of the human (eating, drinking, ...)
        Priority: 2
        input: 6
            map level left, map level right, map level up, map level down,
            water level, food level
        output: 5
            do nothing, go east, go west, go north, go south

    Social Brain:
        This brain is responsible for the human's social skills
        Priority: 1
        input: 5
            normalised distance from next human left, right, up, down,
            normalised population density on the same square
        output: 4
            go east, go west, go north, go south

    Reproduction Brain:
        This brain decides whether or not to reproduce with the closest human
        Priority: 0
        input: 4
            age, other person's age, other person's water level, other person's food level
        output: 2
            yes, no
    """

    def __init__(self):
        self.__survival_brain = NeuralNetwork(input=4, output=5)
        self.__needs_brain = NeuralNetwork(input=6, output=5)
        self.__social_brain = NeuralNetwork(input=5, output=4)
        self.__reproductive_brain = NeuralNetwork(input=4, output=2)

        self.__universal_brain = NeuralNetwork(input=11, output=4, hidden=[11])

        self.x = int(random.random() * WIDTH)
        self.y = int(random.random() * HEIGHT)

        self.water = 1
        self.food = 1
        self.age = 0

    def tick(self):
        self.water -= water_decrease
        self.food -= food_decrease
        self.age += aging

    def is_alive(self, map, population_density, flags=None):
        """
        Flags: check a cause of death or not:
            [disable starving, disable dehydration, disable disease, disable random aging death]
        """
        if flags is None:
            flags = [False, False, False, False]
        if not (0 <= self.x < WIDTH and 0 <= self.y < HEIGHT):
            return False

        if map[self.x, self.y] <= WATER_LEVEL:
            self.water = 1
        else:
            for i in [-1, 1]:
                if (0 <= self.x + i < WIDTH and map[self.x + i, self.y] <= WATER_LEVEL) or \
                        (0 <= self.y + i < HEIGHT and map[self.x, self.y + i] <= WATER_LEVEL):
                    self.water = 1
                    break

        if population_density > 0:
            self.food = 1

        return map[self.x, self.y] > (WATER_LEVEL - drowning) and \
               (1 if flags[3] else random.random()) > self.age and \
               (flags[1] or self.water > 0) and (flags[0] or self.food > 0) and \
               (flags[2] or random.random() > population_density * disease_rate)

    def __survival(self, map_neighboring):
        out = self.__survival_brain.forward(
            map_neighboring
        )

        return np.argmax(out)

    def __needs(self, map_neighboring):
        out = self.__needs_brain.forward(
            map_neighboring + [self.water, self.food]
        )

        return np.argmax(out)

    def __social(self, humans_closest, population_density):
        out = self.__social_brain.forward(
            humans_closest + [population_density]
        )

        return np.argmax(out)

    def __reproduction(self, other_age, other_water, other_food):
        out = self.__reproductive_brain.forward(
            [self.age, other_age, other_water, other_food]
        )

        return np.argmax(out)

    def move(self, map_neighboring, humans_closest, population_density):
        """
        direction = self.__survival(map_neighboring)
        if direction == NOTHING:
            direction = self.__needs(map_neighboring)
            if direction == NOTHING:
                direction = self.__social(humans_closest, population_density)
        """
        direction = np.argmax(self.__universal_brain.forward(
            map_neighboring + humans_closest + [population_density, self.food, self.water]
        ))

        if direction == EAST:
            self.x -= 1
        elif direction == WEST:
            self.x += 1
        elif direction == NORTH:
            self.y -= 1
        else:
            self.y += 1

    def want_reproduce(self, partner):
        return self.__reproduction(partner.age, partner.water, partner.food) == YES

    def reproduce(self, partner, mutation_rate=mutation_rate):
        child = Human()

        """
        child.__survival_brain = self.__survival_brain.reproduce(partner.__survival_brain)
        child.__needs_brain = self.__needs_brain.reproduce(partner.__needs_brain)
        child.__social_brain = self.__social_brain.reproduce(partner.__social_brain)
        child.__reproductive_brain = self.__reproductive_brain.reproduce(partner.__reproductive_brain)

        child.__survival_brain.mutate(mutation_rate)
        child.__needs_brain.mutate(mutation_rate)
        child.__social_brain.mutate(mutation_rate)
        child.__reproductive_brain.mutate(mutation_rate)
        """
        child.__universal_brain = self.__universal_brain.reproduce(partner.__universal_brain)
        child.__universal_brain.mutate(mutation_rate)

        return child
