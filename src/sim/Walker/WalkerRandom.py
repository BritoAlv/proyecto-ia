import random
from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, valid_coordinates
from sim.Walker.PathFinder import PathFinder, WalkerGraphNode
from sim.Walker.WalkerCommon import get_associated_semaphores

class WalkerRandom(PathFinder):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)

    def get_neighbours(self, current: WalkerGraphNode) -> list:
        return []

    def option_semaphor(self, cur_pos : tuple[int, int]):
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
            if isinstance(next_block, RoadBlock):
                streets : list[tuple[int, int]] = []
                while valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], RoadBlock):
                    streets.append((x, y))
                    x += walker_x
                    y += walker_y
                works = True
                if valid_coordinates(x, y, height, width) and isinstance(matrix[x][y], SidewalkBlock):
                    for index, _  in enumerate(streets):
                        semaphores = get_associated_semaphores(streets[index], self.environment)
                        if len(semaphores) == 0:
                            works = False
                            break
                    if works:
                        return streets + [(x,y)]
        return []
                    
    def option_neighbour(self, cur_pos : tuple[int, int]): 
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
         
    def path_finder(self, cur_pos: tuple[int, int], goal: tuple[int, int]):
        option1 = self.option_semaphor(cur_pos)
        option2 = self.option_neighbour(cur_pos)
        if random.random() <= 0.6 and len(option1) > 0:
            return option1
        return option2