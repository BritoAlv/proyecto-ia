from abc import ABC, abstractmethod
import pickle
import random
from threading import Lock, Thread
import time
from uuid import UUID, uuid4
from ui.globals import Directions, valid_coordinates


class Block(ABC):
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates


class SemaphoreBlock(Block):
    def __init__(
        self, coordinates: tuple[int, int], representative: tuple[int, int]
    ) -> None:
        super().__init__(coordinates)
        self.representative = representative


class RoadBlock(Block):
    def __init__(self, coordinates: tuple[int, int], direction: int) -> None:
        super().__init__(coordinates)
        self.direction = direction
        self.car_id: UUID = None


class SidewalkBlock(Block):
    def __init__(self, coordinates: tuple[int, int], vertical: bool) -> None:
        super().__init__(coordinates)
        self.vertical = vertical
        self.walker_id: UUID = None


class Environment:
    def __init__(self, matrix: list[list[Block]]) -> None:
        self.matrix = matrix
        self.cars: dict[UUID, Car] = {}
        self.walkers: dict[UUID, tuple[int, int]] = {}
        self.semaphores: dict[tuple[int, int], int] = {}
        self._add_semaphores()

        self.lock = Lock()

        #######################################
        # Setup InitialCars.
        cars = []
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                if isinstance(self.matrix[i][j], RoadBlock) and random.randint(0, 5) == 0:
                    cars.append(RandomCar((i, j)))

            

        for car in cars:
            self.cars[car.id] = car
        
        #######################################

        #######################################
        # Lines for testing, remove when needed
        thread = Thread(target=self.random_cars)
        thread.daemon = True
        thread.start()
        thread = Thread(target=self.random_semaphores)
        thread.daemon = True
        thread.start()
        #######################################

    def random_cars(self):
        while True:
            time.sleep(0.5)
            with self.lock:
                for car_id in self.cars:
                    self.cars[car_id].move(self)

    def _add_semaphores(self) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]
                if isinstance(block, SemaphoreBlock):
                    self.semaphores[block.representative] = Directions.NORTH

        
    # Method for testing
    def random_semaphores(self):
        while True:
            time.sleep(0.5)
            with self.lock:
                for semaphore_id in self.semaphores:
                    self.semaphores[semaphore_id] = random.choice(
                        [
                            Directions.NORTH,
                            Directions.SOUTH,
                            Directions.EAST,
                            Directions.WEST,
                        ]
                    )


class Car(ABC):
    def __init__(self, current_pos : tuple[int, int]):
        self.current_pos = current_pos
        self.id = uuid4()

    @abstractmethod
    def move(self, environment : Environment):
        pass

class RandomCar(Car):
    def __init__(self, start_pos : tuple[int, int]):
        super().__init__(start_pos)


    def move(self, environment: Environment):
        i, j = self.current_pos
        offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(offsets)

        for m, n in offsets:
            x = i + m
            y = j + n
            if valid_coordinates(x, y, len(environment.matrix), len(environment.matrix[0])): 
                if isinstance(environment.matrix[x][y], RoadBlock):
                    if environment.matrix[i][j].direction == environment.matrix[x][y].direction:
                        self.current_pos = (x, y)
                        return
                if isinstance(environment.matrix[x][y], SemaphoreBlock):
                    representative = environment.matrix[x][y].representative
                    direction = environment.matrix[i][j].direction
                    print(representative, direction)
                    if direction == environment.semaphores[representative]:
                        if direction == Directions.NORTH:
                            self.current_pos = (i, j+2)
                        if direction == Directions.SOUTH:
                            self.current_pos = (i, j-2)
                        if direction == Directions.EAST:
                            self.current_pos = (i-2, j)
                        if direction == Directions.WEST:
                            self.current_pos = (i+2, j)