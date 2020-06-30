import numpy as np
import random

from src.constants import WIDTH, HEIGHT, SEED, NOISE_DECAY, WATER_LEVEL


def __is_water(map, x, y, default=True):
    if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
        return default

    return map[x, y] <= WATER_LEVEL


def post_processing(map):
    # Remove isolated water points or isolated islands
    for x in range(WIDTH):
        for y in range(HEIGHT):
            water = map[x, y] <= WATER_LEVEL
            next_to_water = 0
            for i in [-1, 1]:
                next_to_water += 1 if __is_water(map, x + i, y) else 0
                next_to_water += 1 if __is_water(map, x, y + i) else 0

            if water and next_to_water == 0:
                map[x, y] = WATER_LEVEL + 0.1
            elif not water and next_to_water == 4:
                map[x, y] = WATER_LEVEL - 0.1


def generate():
    # Set the seed
    random.seed(SEED)
    # Initialize the whole map to -1
    map = np.zeros((WIDTH, HEIGHT)) - 1.0

    # Get the corners
    corners = [
        [0, 0], [WIDTH - 1, 0], [0, HEIGHT - 1], [WIDTH - 1, HEIGHT - 1]
    ]
    # Set the corners to random values
    map[corners[0][0], corners[0][1]] = random.random()
    map[corners[1][0], corners[1][1]] = random.random()
    map[corners[2][0], corners[2][1]] = random.random()
    map[corners[3][0], corners[3][1]] = random.random()

    # Apply diamond algorithm
    diamond(map, corners, 1)

    # Offset the map to ensure its values are positive
    map_offset = np.amin(map)
    if map_offset < 0:
        map += map_offset

    # Normalize the map so that its values are between 0 and 1
    map = map / np.amax(map)

    # Apply post-processing
    post_processing(map)

    return map


def get_closest(map, point, direction):
    tmp = [point[0] + direction[0], point[1] + direction[1]]
    if tmp[0] < 0 or tmp[0] >= WIDTH or tmp[1] < 0 or tmp[1] >= HEIGHT:
        return -1

    if map[tmp[0], tmp[1]] < 0:
        return get_closest(map, tmp, direction)
    else:
        return map[tmp[0], tmp[1]]


def is_ended(corners):
    return corners[1][0] <= corners[0][0] + 1 and corners[3][0] <= corners[2][0] + 1 and \
        corners[2][1] <= corners[0][1] + 1 and corners[3][1] <= corners[1][1] + 1


def diamond(map, corners, noise):
    """
    Apply the diamond algorithm to generate an hight map
    :param map: the map to generate
    :param corners: an array where each entry is an array as follow
        [
            top_left_corner[x, y], top_right_corner[x, y],
            bottom_left_corner[x, y], bottom_right_corner[x, y]
        ]
    """
    if is_ended(corners):  # check if the recursion ended
        return

    # Get the point at the center of the rectangle defined by the four corners
    center_point = [
        int((corners[0][0] + corners[3][0]) / 2),
        int((corners[0][1] + corners[3][1]) / 2)
    ]

    # The center point's value is the average of all the corner's values modified by a random value between 0 and 1
    if map[center_point[0], center_point[1]] < 0:
        average_value = sum([
            map[corners[0][0], corners[0][1]],
            map[corners[1][0], corners[1][1]],
            map[corners[2][0], corners[2][1]],
            map[corners[3][0], corners[3][1]]
        ]) / 4
        map[center_point[0], center_point[1]] = average_value + random.random() * noise

    # Get the new points as follow:
    #  C0 *  T  *  C1
    #  *  *  *  *  *
    #  L  *  CP *  R
    #  *  *  *  *  *
    #  C2 *  B  *  C3
    # where C0, C1, C2 and C3 are the four corners and CP the new point generated above (center_point)
    # L, T, R and B are left_point, top_point, right_point and bottom_point
    left_point = [corners[0][0], center_point[1]]
    top_point = [center_point[0], corners[0][1]]
    right_point = [corners[3][0], center_point[1]]
    bottom_point = [center_point[0], corners[3][1]]

    # Set the values of those four newly generated points the same way the center point's value was defined
    if map[left_point[0], left_point[1]] < 0:
        tmp = [
            map[corners[0][0], corners[0][1]],
            map[center_point[0], center_point[1]],
            map[corners[2][0], corners[2][1]]
        ]
        # Check if there is a value to the left of left_point
        # # If so, add it
        val = get_closest(map, left_point, [-1, 0])
        if val >= 0:
            tmp.append(val)
        # Set left_point
        map[left_point[0], left_point[1]] = random.random() * noise + sum(tmp) / len(tmp)

    # top_point:
    if map[top_point[0], top_point[1]] < 0:
        tmp = [
            map[corners[0][0], corners[0][1]],
            map[center_point[0], center_point[1]],
            map[corners[1][0], corners[1][1]]
        ]
        val = get_closest(map, left_point, [0, -1])
        if val >= 0:
            tmp.append(val)
        map[top_point[0], top_point[1]] = random.random() * noise + sum(tmp) / len(tmp)

    # right_point:
    if map[right_point[0], right_point[1]] < 0:
        tmp = [
            map[corners[1][0], corners[1][1]],
            map[center_point[0], center_point[1]],
            map[corners[3][0], corners[3][1]]
        ]
        val = get_closest(map, left_point, [1, 0])
        if val >= 0:
            tmp.append(val)
        map[right_point[0], right_point[1]] = random.random() * noise + sum(tmp) / len(tmp)

    # bottom_point:
    if map[bottom_point[0], bottom_point[1]] < 0:
        tmp = [
            map[corners[2][0], corners[2][1]],
            map[center_point[0], center_point[1]],
            map[corners[3][0], corners[3][1]]
        ]
        val = get_closest(map, left_point, [0, 1])
        if val >= 0:
            tmp.append(val)
        map[bottom_point[0], bottom_point[1]] = random.random() * noise + sum(tmp) / len(tmp)

    # Do the recursion with the newly generated points
    diamond(map, [corners[0], top_point, left_point, center_point], noise * NOISE_DECAY)
    diamond(map, [top_point, corners[1], center_point, right_point], noise * NOISE_DECAY)
    diamond(map, [left_point, center_point, corners[2], bottom_point], noise * NOISE_DECAY)
    diamond(map, [center_point, right_point, bottom_point, corners[3]], noise * NOISE_DECAY)
