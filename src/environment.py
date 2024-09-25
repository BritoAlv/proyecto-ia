from abc import ABC
from threading import Lock
import time
from uuid import UUID
from globals import Directions


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
        self.cars: dict[UUID, tuple[int, int]] = {}
        self.walkers: dict[UUID, tuple[int, int]] = {}
        self.semaphores: dict[tuple[int, int], int] = {}
        self._add_semaphores()
        self.lock = Lock()

    def _add_semaphores(self) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]
                if isinstance(block, SemaphoreBlock):
                    self.semaphores[block.representative] = Directions.NORTH