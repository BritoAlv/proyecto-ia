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
    def __init__(self, coordinates: tuple[int, int]) -> None:
        super().__init__(coordinates)
        self.light = Directions.NORTH

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

        self.lock = Lock()

        #######################################
        # Lines for testing, remove when needed
        thread = Thread(target=self.random_cars)
        thread.daemon = True
        thread.start()
        #######################################

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
                                    block.car_id = None
