from abc import ABC, abstractmethod
import time
from environment import Environment
import random
from uuid import uuid4

from environment import RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import Directions, valid_coordinates


class Agent(ABC):
    def __init__(self, id, environment : Environment):
        self.id = id
        self.environment = environment

    @abstractmethod
    def act(self) -> None:
        pass


class MovingAgent(Agent, ABC):
    def __init__(self, position, environment: Environment):
        super().__init__(uuid4(), environment)
        self.position = position


class Semaphore(Agent):
    def act(self) -> None:
        while True:
            time.sleep(0.5)

            with self.environment.lock:
                light_directions = [
                    Directions.NORTH, 
                    Directions.SOUTH, 
                    Directions.EAST, 
                    Directions.WEST
                ]

                self.environment.semaphores[self.id] = random.choice(light_directions)
        

class Car(MovingAgent):
    def act(self) -> None:
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        while True:
            time.sleep(0.5)

            i, j = self.position
            current_block = matrix[i][j]

            with self.environment.lock:
                offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                random.shuffle(offsets)

                for p, q in offsets:
                    x = i + p
                    y = j + q

                    if not valid_coordinates(x, y, height, width):
                        continue

                    next_block = matrix[x][y]
                    if isinstance(next_block, RoadBlock) and next_block.car_id == None:
                        next_block.car_id = self.id
                        current_block.car_id = None
                        self.environment.cars[self.id] = x, y
                        self.position = x, y
                        break


class Walker(MovingAgent):
    def act(self) -> None:
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        while True:
            time.sleep(0.5)

            i, j = self.position
            current_block = matrix[i][j]

            with self.environment.lock:
                offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                random.shuffle(offsets)

                for p, q in offsets:
                    x = i + p
                    y = j + q

                    if not valid_coordinates(x, y, height, width):
                        continue

                    next_block = matrix[x][y]
                    if isinstance(next_block, SidewalkBlock) and next_block.walker_id == None:
                        next_block.walker_id = self.id
                        current_block.walker_id = None
                        self.environment.walkers[self.id] = x, y
                        self.position = x, y
                        break