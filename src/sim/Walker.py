from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, valid_coordinates
from sim.Car.CarCommon import check_free
from sim.MovingAgent import MovingAgent


import random


class Walker(MovingAgent):

    def __init__(self, position, environment: Environment, gui_label):
        super().__init__(position, environment, gui_label)
        self.path = []

    def set_walker_pos(self, new: tuple[int, int]):
        i, j = self.position
        x, y = new
        assert(abs(i-x)+ abs(j -y) in [1, 0])
        self.position = new

    def update_path(self):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        i, j = self.position
        offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        random.shuffle(offsets)

        for walker_x, walker_y in offsets:
            x = i + walker_x
            y = j + walker_y

            if not valid_coordinates(x, y, height, width):
                continue

            next_block = matrix[x][y]
            if isinstance(next_block, SidewalkBlock):
                self.path = [(x, y)]
                break

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
                        self.path = streets + [(x,y)]
                        return

    def act(self) -> None:
        if len(self.path) == 0:
            self.update_path()
        if len(self.path) > 0:
            self.set_walker_pos(self.path.pop(0))