from environment import RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent


import random
import time


class Car(MovingAgent):
    def __init__(self, position, environment):
        super().__init__(position, environment)
        self.sleep_time = 0.5 + random.random()

    def act(self) -> None:

        def check_free(i, j):
            return isinstance(self.environment.matrix[i][j], RoadBlock) and self.environment.matrix[i][j].car_id == None

        def set_car_pos(i, j, x, y, id):
            self.environment.matrix[i][j].car_id = None
            self.environment.matrix[x][y].car_id = id
            self.environment.cars[id] = (x, y)
            self.position = (x, y)

        while True:
            time.sleep(self.sleep_time)
            i, j = self.position
            with self.environment.lock:
                offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                random.shuffle(offsets)

                for t in offsets:
                    m = t[0]
                    n = t[1]
                    x = i + m
                    y = j + n
                    if valid_coordinates(x, y, len(self.environment.matrix), len(self.environment.matrix[0])):
                        if isinstance(self.environment.matrix[x][y], RoadBlock):
                            new_direction_offset = DIRECTION_OFFSETS[self.environment.matrix[x][y].direction]
                            if new_direction_offset == (m, n):
                                if check_free(x, y):
                                    set_car_pos(i, j, x, y, self.id)
                                    break
                        if isinstance(self.environment.matrix[x][y], SemaphoreBlock):
                            representative = self.environment.matrix[x][y].representative
                            direction = self.environment.matrix[i][j].direction
                            if direction == self.environment.semaphores[representative]:
                                new_pos = self.pos_cross_semaphor(x, y, direction)
                                if check_free(new_pos[0], new_pos[1]):
                                    set_car_pos(i, j, new_pos[0], new_pos[1], self.id)
                                    break

    def pos_cross_semaphor(self, i, j, direction) -> tuple[int, int]:
        r = i
        c = j

        while(valid_coordinates(r, c, len(self.environment.matrix), len(self.environment.matrix[0])) and isinstance(self.environment.matrix[r][c], SemaphoreBlock)):
            if direction == Directions.NORTH:
                r -= 1
            if direction == Directions.SOUTH:
                r += 1
            if direction == Directions.EAST:
                c -= 1
            if direction == Directions.WEST:
                c += 1

        if(valid_coordinates(r, c, len(self.environment.matrix), len(self.environment.matrix[0])) and isinstance(self.environment.matrix[r][c], RoadBlock)):
            return (r, c)

        return (i, j)