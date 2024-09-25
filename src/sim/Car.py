from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent


import random
import time


class Car(MovingAgent):
    def __init__(self, position : tuple[int, int], goal : tuple[int, int], environment : Environment):
        super().__init__(position, environment)
        self.next_positions: list[tuple[int, int]] = []
        self.attempts: int = 0
        self.goal : tuple[int, int] = goal

    def check_free(self, i, j):
        return (
            isinstance(self.environment.matrix[i][j], RoadBlock)
            and self.environment.matrix[i][j].car_id == None
        )

    def set_car_pos(self, i, j, x, y, id):
        self.environment.matrix[i][j].car_id = None
        self.environment.matrix[x][y].car_id = id
        self.environment.cars[id] = (x, y)
        self.position = (x, y)

    def update_list(self):
        """
        If the car doesn't move after two attempts delete this strategy.
        """
        if self.attempts >= 3:
            self.next_positions = []

        """
        With probability 0.4 update the list to use a new one.
        """
        if random.random() < 0.2:
            self.next_positions = []

    def act(self) -> None:
        while True:
            time.sleep(self.sleep_time) # clock race 
            i, j = self.position
            with self.environment.lock:
                if self.position == self.goal: # car reached goal so done.
                    self.environment.matrix[i][j].car_id = None
                    self.environment.cars.pop(self.id)
                    return
                offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
                direction = self.environment.matrix[i][j].direction
                self.update_list()
                if len(self.next_positions) > 0:
                    # use top position for moving
                    next_pos = self.next_positions[0]
                    x = next_pos[0]
                    y = next_pos[1]

                    car_moved = False

                    # Check if cell is free and its valid.
                    if self.check_valid(x, y, RoadBlock) and self.check_free(x, y):
                        # Case 1 : there is a semaphore from (i, j) to (x, y)
                        if self.check_valid(
                            i + offset[0], j + offset[1], SemaphoreBlock
                        ):
                            representative = self.environment.matrix[x][
                                y
                            ].representative
                            if direction == self.environment.semaphores[representative]:
                                if new_pos in self.semaphore_options(
                                    i + offset[0], j + offset[1], direction
                                ):
                                    self.set_car_pos(
                                        i, j, new_pos[0], new_pos[1], self.id
                                    )
                                    car_moved = True
                        # Case 2: (i, j) to (x, y)
                        else:
                            if x - i == offset[0] and y - j == offset[1]:
                                self.set_car_pos(i, j, x, y, self.id)
                                car_moved = True

                    if not car_moved:
                        self.attempts += 1
                    else:
                        self.next_positions.pop(0)

                else:
                    # use random moving to obtain next position
                    m = offset[0]
                    n = offset[1]
                    x = i + m
                    y = j + n
                    if self.check_valid(x, y, RoadBlock):
                        if self.check_free(x, y):
                            self.set_car_pos(i, j, x, y, self.id)
                    elif self.check_valid(x, y, SemaphoreBlock):
                        representative = self.environment.matrix[x][y].representative
                        if direction == self.environment.semaphores[representative]:
                            new_pos = self.pos_cross_semaphor(x, y, direction)
                            if self.check_free(new_pos[0], new_pos[1]):
                                self.set_car_pos(i, j, new_pos[0], new_pos[1], self.id)

    def pos_cross_semaphor(self, i, j, direction) -> tuple[int, int]:
        r = i
        c = j
        options = [(i, j)] + self.semaphor_options(r, c, direction)
        return options[random.randint(0, len(options) - 1)]

    def check_valid(self, x, y, class_instance):
        return valid_coordinates(
            x, y, len(self.environment.matrix), len(self.environment.matrix[0])
        ) and isinstance(self.environment.matrix[x][y], class_instance)

    def check_option(self, r, c, offset) -> list[tuple[int, int]]:
        options = []
        dx = offset[0]
        dy = offset[1]
        rr = r + dx
        cc = c + dy

        while self.check_valid(rr, cc, SemaphoreBlock):
            rr += dx
            cc += dy

        if self.check_valid(rr, cc, RoadBlock):
            if DIRECTION_OFFSETS[self.environment.matrix[rr][cc].direction] == offset:
                options.append((rr, cc))
        return options

    def semaphor_options(
        self, r: int, c: int, direction: Directions
    ) -> list[tuple[int, int]]:
        options = []
        while self.check_valid(r, c, SemaphoreBlock):
            if direction == Directions.NORTH or direction == Directions.SOUTH:
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.EAST])
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.WEST])
                if direction == Directions.NORTH:
                    r -= 1
                if direction == Directions.SOUTH:
                    r += 1
            else:
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.NORTH])
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.SOUTH])
                if direction == Directions.EAST:
                    c -= 1
                if direction == Directions.WEST:
                    c += 1

        if self.check_valid(r, c, RoadBlock):
            options.append((r, c))

        return options
