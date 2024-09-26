from abc import ABC
from threading import Lock
import time
from uuid import UUID
from globals import Directions


class Block(ABC):
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates

class PlaceBlock(Block):
    def __init__(self, coordinates: tuple[int, int], name : str, description : str, representative : tuple[int, int]) -> None:
        super().__init__(coordinates)
        self.name = name
        self.description = description
        self.representative = representative 

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

        from sim.Car import Car
        self.cars: dict[UUID, Car] = {}
        
        from sim.Walker import Walker
        self.walkers: dict[UUID, Walker] = {}

        from sim.Semaphore import Semaphore
        self.semaphores: dict[tuple[int, int], Semaphore] = {}

        self._add_semaphores()
        self.lock = Lock()

    def _add_semaphores(self) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]
                if isinstance(block, SemaphoreBlock) and block.representative not in self.semaphores:
                    from sim.Semaphore import Semaphore
                    self.semaphores[block.representative] = Semaphore(block.representative, self)
                    self.semaphores[block.representative].gui_label = len(self.semaphores)