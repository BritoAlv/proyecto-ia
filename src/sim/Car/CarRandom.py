from environment import RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarCommon import check_valid, pos_cross_semaphor
from sim.Car.CarGraphNode import CarGraphNode, PathFinder


class CarRandom(PathFinder):
    def algorithm(self, cur_pos: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        # use random moving to obtain next position
        i, j = cur_pos
        offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
        direction = self.environment.matrix[i][j].direction
        m = offset[0]
        n = offset[1]
        x = i + m
        y = j + n
        if check_valid(x, y, RoadBlock, self.environment):
            return [(x, y)]
        elif check_valid(x, y, SemaphoreBlock, self.environment):
            representative = self.environment.matrix[x][y].representative
            if direction == self.environment.semaphores[representative].current:
                return pos_cross_semaphor(x, y, direction, self.environment)
        return []
                

    def get_neighbours(self, current: CarGraphNode) -> list[CarGraphNode]:
        raise NotImplementedError