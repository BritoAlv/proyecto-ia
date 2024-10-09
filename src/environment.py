from abc import ABC
from datetime import datetime, timedelta
import random
from uuid import UUID

from globals import valid_coordinates
from stats import Stats


class Block(ABC):
    def __init__(self, coordinates: tuple[int, int]) -> None:
        self.coordinates = coordinates


class PlaceBlock(Block):
    def __init__(self, coordinates: tuple[int, int], name: str, description: str, representative: tuple[int, int], meta_data: dict = None) -> None:
        super().__init__(coordinates)
        self.name = name
        self.description = description
        self.representative = representative
        self.meta_data: dict = meta_data


class SemaphoreBlock(Block):
    def __init__(self, coordinates: tuple[int, int], representative: tuple[int, int]) -> None:
        super().__init__(coordinates)
        self.representative = representative


class RoadBlock(Block):
    def __init__(self, coordinates: tuple[int, int], direction: int) -> None:
        super().__init__(coordinates)
        self.direction = direction
        self.car_id: UUID = None
        self.walkers_id: list[UUID] = []


class SidewalkBlock(Block):
    def __init__(self, coordinates: tuple[int, int], vertical: bool) -> None:
        super().__init__(coordinates)
        self.vertical = vertical
        self.walkers_id: list[UUID] = []


class Environment:
    def __init__(self, name, matrix: list[list[Block]], start_date: datetime = datetime(2000, 1, 1), use_fuzzy: bool = True) -> None:
        # Local imports
        from sim.Car.Car import Car
        from sim.Semaphor.Semaphore import Semaphore
        from sim.Walker.Walker import Walker

        # Core logic properties
        self.matrix = matrix
        self.name = name
        self.cars: dict[UUID, Car] = {}
        self.walkers: dict[UUID, Walker] = {}
        self.semaphores: dict[tuple[int, int], Semaphore] = {}
        self.start_date: datetime = start_date
        self.date: datetime = start_date
        self.weather: float = 0
        self.places: dict[tuple[int, int], PlaceBlock] = {}
        self.stats: Stats = Stats()
        self._extract_data(use_fuzzy)  # Extract

        self.sidewalk_blocks = self._get_type_blocks(SidewalkBlock)
        self.place_blocks = self._get_type_blocks(PlaceBlock)
        self.road_blocks = self._get_type_blocks(RoadBlock)

        # Testing purpose call
        self._initialize()

    def get_free_blocks(self, block_type: type):
        matrix = self.matrix
        height = len(matrix)
        width = len(matrix[0])
        free_blocks: list[RoadBlock] = []

        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, block_type):
                    if block_type == RoadBlock and block.car_id == None:
                        free_blocks.append(block)
                    elif block_type == SidewalkBlock:
                        free_blocks.append(block)
        return free_blocks

    def _get_type_blocks(self, block_type: type) -> list:
        matrix = self.matrix
        height = len(matrix)
        width = len(matrix[0])

        blocks: list[block_type] = []
        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, block_type):
                    blocks.append(block)
        return blocks

    def _extract_data(self, use_fuzzy: bool) -> None:
        height = len(self.matrix)
        width = len(self.matrix[0])

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]

                # Extract semaphores representatives
                if isinstance(block, SemaphoreBlock) and block.representative not in self.semaphores:
                    from sim.Semaphor.Semaphore import Semaphore

                    self.semaphores[block.representative] = Semaphore(block.representative, self, len(self.semaphores), use_fuzzy)

                # Extract interest places
                if isinstance(block, PlaceBlock):
                    self.places[(i, j)] = block

        for i in range(height):
            for j in range(width):
                block = self.matrix[i][j]
                if isinstance(block, RoadBlock):
                    dx = [-1, 1, 0, 0]
                    dy = [0, 0, -1, 1]
                    for x, y in zip(dx, dy):
                        if valid_coordinates(i + x, j + y, len(self.matrix), len(self.matrix[0])):
                            if isinstance(self.matrix[i + x][j + y], SemaphoreBlock):
                                self.semaphores[self.matrix[i + x][j + y].representative].add_direction(block.direction)

    # Testing purpose method
    def _initialize(self):
        from sim.Car.Car import Car
        from sim.Walker.Walker import Walker

        for _ in range(20):
            if len(self.get_free_blocks(RoadBlock)) > 0:
                goal = random.choice(self.road_blocks).coordinates
                _ = Car(goal, self)
            if len(self.place_blocks) > 0:
                places = random.choices(self.place_blocks, k=random.randint(1, len(self.place_blocks)))
                _ = Walker(places, self)

    def increase_date(self, seconds: int = 1):
        previous_day = self.date.day
        self.date += timedelta(seconds=seconds)
        next_day = self.date.day

        if previous_day != next_day:
            self.update_weather()

    def update_weather(self):
        self.weather = random.uniform(0, 0.4)
