from abc import ABC
import pickle
import random
from threading import Lock, Thread
import time
from uuid import UUID, uuid4
from globals import Directions

class Block():
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

        thread = Thread(target=self.random_cars)
        thread.daemon = True
        thread.start()

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


# m = [` 
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [5, 5, 5, -1, -1, 5, 5, 5, 5, -1, -1, 5, 5, 5, 5, -1, -1, 5, 5, 5],
#     [4, 4, 4, -1, -1, 4, 4, 4, 4, -1, -1, 4, 4, 4, 4, -1, -1, 4, 4, 4],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [5, 5, 5, -1, -1, 5, 5, 5, 5, -1, -1, 5, 5, 5, 5, -1, -1, 5, 5, 5],
#     [4, 4, 4, -1, -1, 4, 4, 4, 4, -1, -1, 4, 4, 4, 4, -1, -1, 4, 4, 4],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0],
#     [0, 0, 0, 7, 2, 0, 0, 0, 0, 2, 7, 0, 0, 0, 0, 2, 7, 0, 0, 0]
# ]


# matrix : list[list[Block]] = []

# height = len(m)
# width = len(m[0])

# for i in range(height):
#     matrix.append([])
#     for j in range(width):
#         if m[i][j] == -1:
#             matrix[i].append(SemaphoreBlock((i, j)))
#         elif m[i][j] != 0:
#             matrix[i].append(RoadBlock((i, j), m[i][j]))
#         else:
#             matrix[i].append(None)

# with open("blocks.pkl", 'wb') as file:
#     pickle.dump(matrix, file)`
    
# e = Environment(matrix)