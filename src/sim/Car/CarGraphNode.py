from abc import ABC, abstractmethod
from environment import Environment
from globals import Directions

class CarGraphNode:
    def __init__(
        self, pos: tuple[int, int], direction: Directions, parent : 'CarGraphNode' ) -> None:
        self.pos = pos
        self.direction = direction
        self.score = 0
        self.parent : None | 'CarGraphNode' = parent

    def __hash__(self) -> int:
        return self.pos.__hash__()

    def __eq__(self, value: object) -> bool:
        return isinstance(value, CarGraphNode) and self.pos == value.pos

    def __lt__(self, value : object) -> bool:
        return isinstance(value, CarGraphNode) and self.score < value.score
    

class PathFinder(ABC):
    def __init__(self, environment : Environment) -> None:
        self.environment = environment
    
    @abstractmethod
    def algorithm(self, cur_pos : tuple[int, int], goal : tuple[int, int]) -> list[tuple[int, int]]:
        pass

    @abstractmethod
    def get_neighbours(self, current : CarGraphNode) -> list[(CarGraphNode, float)]:
        pass