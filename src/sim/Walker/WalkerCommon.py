import random
from environment import Environment, SemaphoreBlock
from globals import DIRECTION_OFFSETS, valid_coordinates
from sim.Semaphor.Semaphore import Semaphore


def get_associated_semaphores(position : tuple[int, int], environment : Environment) -> list[Semaphore]:
        result = []
        i, j = position
        offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(offsets)
        for dx, dy in offsets:
            if not valid_coordinates( i + dx, j + dy, len(environment.matrix), len(environment.matrix[0])) or not isinstance(environment.matrix[i + dx][j + dy], SemaphoreBlock):
                        continue
            result.append( environment.semaphores[environment.matrix[i + dx][j + dy].representative])
        return result