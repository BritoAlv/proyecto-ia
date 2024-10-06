import random
from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, valid_coordinates
from sim.Walker.PathFinder import PathFinder, WalkerGraphNode

class WalkerRandom(PathFinder):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

    def get_neighbours(self, current: WalkerGraphNode) -> list:
        return []

    def path_finder(self, cur_pos: tuple[int, int], goal: tuple[int, int]):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        i, j = cur_pos
        offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(offsets)
        
        for walker_x, walker_y in offsets:
            x = i + walker_x
            y = j + walker_y
            if not valid_coordinates(x, y, height, width):
                continue

            next_block = matrix[x][y]
            if isinstance(next_block, SidewalkBlock):
                return [(x, y)]

            if isinstance(next_block, RoadBlock):
                streets : list[tuple[int, int]] = []
                while valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], RoadBlock):
                    streets.append((x, y))
                    x += walker_x
                    y += walker_y
                works = True
                if valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], SidewalkBlock):
                    for index, st  in enumerate(streets):
                        current_block = matrix[st[0]][st[1]]
                        p, q = DIRECTION_OFFSETS[current_block.direction]
                        sem_x = st[0] + p
                        sem_y = st[1] + q
                        if not valid_coordinates(sem_x, sem_y, height, width) or not isinstance(matrix[sem_x][sem_y], SemaphoreBlock):
                            works = False
                            break
                        semaphore = self.environment.semaphores[matrix[sem_x][sem_y].representative]
                        if semaphore.current == current_block.direction or semaphore.time_till_change() < index + 1:
                            works = False
                            break
                    if works:
                        return streets + [(x,y)]