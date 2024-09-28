from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarCommon import check_free, check_valid, semaphor_options
from sim.Car.CarStrategy import CarStrategy
from sim.MovingAgent import MovingAgent

class Car(MovingAgent):
    def __init__(
        self, position: tuple[int, int], goal: tuple[int, int], environment: Environment, gui_label):
        super().__init__(position, environment, gui_label)
        self.goal: tuple[int, int] = goal
        self.strategy = CarStrategy(environment)

    def set_car_pos(self, i, j, x, y, id):
        self.environment.matrix[i][j].car_id = None
        self.environment.matrix[x][y].car_id = id
        self.environment.cars[id] = self
        self.position = (x, y)

    def remove_car(self):
        i, j = self.position
        self.environment.matrix[i][j].car_id = None
        self.environment.cars.pop(self.id)

    def act(self) -> None:
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
                        self.set_car_pos(i, j, next_pos[0], next_pos[1], self.id)
            # Case 2: (i, j) to (x, y)
            else:
                if x - i == offset[0] and y - j == offset[1]:
                    self.set_car_pos(i, j, x, y, self.id)