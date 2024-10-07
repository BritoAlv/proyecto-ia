from environment import Environment


from abc import ABC, abstractmethod

from globals import Directions

class WalkerGraphNode:
    def __init__(
        self, pos: tuple[int, int], parent : 'WalkerGraphNode', cross_direction = None ) -> None:
        self.pos = pos
        self.score = 0
        self.parent : None | 'WalkerGraphNode' = parent
        self.cross_direction = cross_direction

    def __hash__(self) -> int:
        return self.pos.__hash__()

    def __eq__(self, value: object) -> bool:
        return isinstance(value, WalkerGraphNode) and self.pos == value.pos

    def __lt__(self, value : object) -> bool:
        return isinstance(value, WalkerGraphNode) and self.score < value.score

class PathFinder(ABC):
    def __init__(self, environment : Environment) -> None:
        self.environment = environment

    @abstractmethod
    def path_finder(self, cur_pos : tuple[int, int], goal : tuple[int, int]):
        pass

    @abstractmethod
    def get_neighbours(self, current : WalkerGraphNode) -> list[(WalkerGraphNode, float)]:
        pass