import random
from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates

def check_free(i : int, j : int, environment : Environment):
        return (
            isinstance(environment.matrix[i][j], RoadBlock)
            and environment.matrix[i][j].car_id == None
        )

def check_valid(x : int, y : int, class_instance, environment : Environment):
    return valid_coordinates(x, y, len(environment.matrix), len(environment.matrix[0])
    ) and isinstance(environment.matrix[x][y], class_instance)

def pos_cross_semaphor(i : int, j : int, direction : Directions,  environment : Environment) -> list[tuple[int, int]]:
    r = i
    c = j
    options = semaphor_options(r, c, direction, environment)
    random.shuffle(options)
    for opt in options:
        if check_free(opt[0], opt[1], environment):
            return [opt]
    return []


def check_option(r, c, offset, environment : Environment) -> list[tuple[int, int]]:
    options = []
    dx = offset[0]
    dy = offset[1]
    rr = r + dx
    cc = c + dy

    while check_valid(rr, cc, SemaphoreBlock, environment):
        rr += dx
        cc += dy

    if check_valid(rr, cc, RoadBlock, environment):
        if DIRECTION_OFFSETS[environment.matrix[rr][cc].direction] == offset:
            options.append((rr, cc))
    return options

def semaphor_options(r: int, c: int, direction: Directions, environment : Environment) -> list[tuple[int, int]]:
    options = []
    while check_valid(r, c, SemaphoreBlock, environment):
        if direction == Directions.NORTH or direction == Directions.SOUTH:
            options += check_option(r, c, DIRECTION_OFFSETS[Directions.EAST], environment)
            options += check_option(r, c, DIRECTION_OFFSETS[Directions.WEST], environment)
            if direction == Directions.NORTH:
                r -= 1
            if direction == Directions.SOUTH:
                r += 1
        else:
            options += check_option(r, c, DIRECTION_OFFSETS[Directions.NORTH], environment)
            options += check_option(r, c, DIRECTION_OFFSETS[Directions.SOUTH], environment)
            if direction == Directions.EAST:
                c += 1
            if direction == Directions.WEST:
                c -= 1

    if check_valid(r, c, RoadBlock, environment):
        options.append((r, c))

    return options