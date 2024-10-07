import random
from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarCommon import check_free, check_valid, pos_cross_semaphor, semaphor_options
from sim.Car.CarStrategy import CarStrategy
from sim.MovingAgent import MovingAgent


class Car(MovingAgent):
    def __init__(self, goal : tuple[int, int], environment: Environment):
        # Validate there's at least one free block
        free_blocks = environment.get_free_blocks(RoadBlock)
        if len(free_blocks) == 0:
            return
        
        position = random.choice(free_blocks).coordinates
        gui_label = len(environment.cars)
        super().__init__(position, environment, gui_label)

        self.environment.matrix[self.position[0]][self.position[1]].car_id = self.id
        self.environment.cars[self.id] = self

        self.goal: tuple[int, int] = goal
        self.strategy = CarStrategy(environment)
        self.total_time_overall = 0
        self.semaphor_time_over_all = 0
        self.semaphor_stuck = 0
        self.semaphor_pos = None

    def set_car_pos(self, new_pos: tuple[int, int]):
        i, j = self.position
        x, y = new_pos
        self.environment.matrix[i][j].car_id = None
        self.environment.matrix[x][y].car_id = id
        self.environment.cars[self.id] = self
        self.position = (x, y)

        if self.semaphor_pos != None:
            self.environment.semaphores[self.semaphor_pos].car_times.append(self.semaphor_stuck)
            self.semaphor_time_over_all += self.semaphor_stuck
            self.semaphor_stuck = 0
            self.semaphor_pos = None

    def update_times(self):
        self.total_time_overall += 1

    def remove_car(self):
        i, j = self.position
        self.environment.matrix[i][j].car_id = None
        self.environment.cars.pop(self.id)
        self.environment.stats.cars_delay.append(self.total_time_overall)
        self.environment.stats.cars_semaphore_delay.append(self.semaphor_time_over_all)

    def act(self) -> None:
        self.update_times()
        if self.position == self.goal:  # car reached goal so done.
            self.remove_car()
            return

        self.strategy.update(self.position, self.goal)
        next_pos = self.strategy.next_pos()
        x, y = next_pos
        i, j = self.position
        offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
        direction = self.environment.matrix[i][j].direction
        # Check if cell is free and its valid.
        if check_valid(x, y, RoadBlock, self.environment) and check_free(x, y, self.environment):
            # Case 1 : there is a semaphore from (i, j) to (x, y)
            sem_x = i + offset[0]
            sem_y = j + offset[1]
            if check_valid(sem_x, sem_y, SemaphoreBlock, self.environment):
                representative = self.environment.matrix[sem_x][sem_y].representative
                if direction == self.environment.semaphores[representative].current:
                    if next_pos in semaphor_options(sem_x, sem_y, direction, self.environment):
                        self.semaphor_pos = representative
                        self.set_car_pos(next_pos)
                        return
            # Case 2: (i, j) to (x, y)
            else:
                if x - i == offset[0] and y - j == offset[1]:
                    self.set_car_pos((x, y))
                    return
        self.emergency_act()

    def emergency_act(self):
        i, j = self.position
        offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
        direction = self.environment.matrix[i][j].direction
        m = offset[0]
        n = offset[1]
        x = i + m
        y = j + n
        if check_valid(x, y, RoadBlock, self.environment):
            self.set_car_pos((x, y))
            self.strategy.path = []
            return
        elif check_valid(x, y, SemaphoreBlock, self.environment):
            representative = self.environment.matrix[x][y].representative
            if direction == self.environment.semaphores[representative].current:
                options = pos_cross_semaphor(x, y, direction, self.environment)
                if len(options) > 0:
                    self.semaphor_pos = representative
                    self.set_car_pos(options[0])
                    self.strategy.path = []
                    return

        self.semaphor_stuck += 1