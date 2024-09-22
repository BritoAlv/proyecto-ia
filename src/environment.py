from abc import ABC
import pickle
import random
from threading import Lock, Thread
import time
from uuid import UUID, uuid4
from ui.globals import Directions

class Block(ABC):
    def __init__(self, coordinates : tuple[int, int]) -> None:
        self.coordinates = coordinates

class SemaphoreBlock(Block):
    def __init__(self, coordinates: tuple[int, int], representative : tuple[int, int]) -> None:
        super().__init__(coordinates)
        self.representative = representative

class RoadBlock(Block):
    def __init__(self, coordinates: tuple[int, int], direction : int) -> None:
        super().__init__(coordinates)
        self.direction = direction
        self.car_id : UUID = None

class SidewalkBlock(Block):
    def __init__(self, coordinates: tuple[int, int], vertical : bool) -> None:
        super().__init__(coordinates)
        self.vertical = vertical
        self.walker_id : UUID = None

class Environment:
    def __init__(self, matrix : list[list[Block]]) -> None:
        self.matrix = matrix
        self.cars : dict[UUID, tuple[int, int]] = {}
        self.walkers : dict[UUID, tuple[int, int]] = {}
        self.semaphores : dict[tuple[int, int], int] = {}
        self._add_semaphores()

        self.lock = Lock()

        #######################################
        # Lines for testing, remove when needed
        thread = Thread(target=self.random_cars)
        thread.daemon = True
        thread.start()
        thread = Thread(target=self.random_semaphores)
        thread.daemon = True
        thread.start()
        #######################################

    def _add_semaphores(self) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]
                if isinstance(block, SemaphoreBlock):
                    self.semaphores[block.representative] = Directions.NORTH

    # Method for testing
    def random_cars(self):
        height = len(self.matrix)
        width = len(self.matrix[0])

        while(True):
            time.sleep(1)
            with self.lock:
                for i in range(height):
                    for j in range(width):
                        if isinstance(self.matrix[i][j], RoadBlock):
                            block = self.matrix[i][j]
                            if bool(random.randint(0, 1)):
                                car_id = uuid4()
                                if block.car_id != None:
                                    self.cars.pop(block.car_id)
                                block.car_id = car_id
                                self.cars[car_id] = (i, j)
                            else:
                                if block.car_id != None:
                                    self.cars.pop(block.car_id)
                                    block.car_id = None# Method for testing
    def random_cars(self):
        height = len(self.matrix)
        width = len(self.matrix[0])

        while(True):
            time.sleep(0.5)
            with self.lock:
                for i in range(height):
                    for j in range(width):
                        if isinstance(self.matrix[i][j], RoadBlock):
                            block = self.matrix[i][j]
                            if bool(random.randint(0, 1)):
                                car_id = uuid4()
                                if block.car_id != None:
                                    self.cars.pop(block.car_id)
                                block.car_id = car_id
                                self.cars[car_id] = (i, j)
                            else:
                                if block.car_id != None:
                                    self.cars.pop(block.car_id)
                                    block.car_id = None

    # Method for testing
    def random_semaphores(self):
        while(True):
            time.sleep(0.5)
            with self.lock:
                for semaphore_id in self.semaphores:
                    self.semaphores[semaphore_id] = random.choice([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])