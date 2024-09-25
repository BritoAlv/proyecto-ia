from environment import RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent


import random
import time


class Car(MovingAgent):
    def __init__(self, position, environment):
        super().__init__(position, environment)

    def act(self) -> None:

        def check_free(i, j):
            return (
                isinstance(self.environment.matrix[i][j], RoadBlock)
                and self.environment.matrix[i][j].car_id == None
            )

        def set_car_pos(i, j, x, y, id):
            self.environment.matrix[i][j].car_id = None
            self.environment.matrix[x][y].car_id = id
            self.environment.cars[id] = (x, y)
            self.position = (x, y)

        while True:
            time.sleep(self.sleep_time)
            i, j = self.position
            with self.environment.lock:
                offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
                m = offset[0]
                n = offset[1]
                x = i + m
                y = j + n
                if valid_coordinates(x, y, len(self.environment.matrix), len(self.environment.matrix[0])):
                    if isinstance(self.environment.matrix[x][y], RoadBlock):
                        if check_free(x, y):
                            set_car_pos(i, j, x, y, self.id)
                    elif isinstance(self.environment.matrix[x][y], SemaphoreBlock):
                        representative = self.environment.matrix[x][y].representative
                        direction = self.environment.matrix[i][j].direction
                        if direction == self.environment.semaphores[representative]:
                            new_pos = self.pos_cross_semaphor(x, y, direction)
                            if check_free(new_pos[0], new_pos[1]):
                                set_car_pos(i, j, new_pos[0], new_pos[1], self.id)

    def pos_cross_semaphor(self, i, j, direction) -> tuple[int, int]:
        r = i
        c = j

        def check_option(offset):
            dx = offset[0]
            dy = offset[1]
            rr = r + dx
            cc = c + dy

            while valid_coordinates(rr, cc, len(self.environment.matrix), len(self.environment.matrix[0])) and isinstance(self.environment.matrix[rr][cc], SemaphoreBlock):
                rr += dx
                cc += dy

            if valid_coordinates(rr, cc, len(self.environment.matrix), len(self.environment.matrix[0])) and isinstance(self.environment.matrix[rr][cc], RoadBlock):
                if (DIRECTION_OFFSETS[self.environment.matrix[rr][cc].direction]== offset):
                    options.append((rr, cc))

        options = [(i, j)]
        while valid_coordinates(
            r, c, len(self.environment.matrix), len(self.environment.matrix[0])
        ) and isinstance(self.environment.matrix[r][c], SemaphoreBlock):
            if direction == Directions.NORTH or direction == Directions.SOUTH:
                check_option(DIRECTION_OFFSETS[Directions.EAST])
                check_option(DIRECTION_OFFSETS[Directions.WEST])
                if direction == Directions.NORTH:
                    r -= 1
                if direction == Directions.SOUTH:
                    r += 1
            else:
                check_option(DIRECTION_OFFSETS[Directions.NORTH])
                check_option(DIRECTION_OFFSETS[Directions.SOUTH])
                if direction == Directions.EAST:
                    c -= 1
                if direction == Directions.WEST:
                    c += 1

        if valid_coordinates(
            r, c, len(self.environment.matrix), len(self.environment.matrix[0])
        ) and isinstance(self.environment.matrix[r][c], RoadBlock):
            options.append((r, c))
        return options[random.randint(0, len(options) - 1)]