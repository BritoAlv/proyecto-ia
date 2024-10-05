from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarCommon import check_valid, pos_cross_semaphor
from sim.Car.CarRandom import CarRandom
from sim.Car.CarDepthDFS import DepthDFS
from sim.Car.CarDijkstra import Dijkstra
from sim.Car.CarDijkstraM import DijkstraM
from sim.Car.CarGraphNode import PathFinder
from sim.Car.Strategy_Fsa import Strategy_Fsa


class CarStrategy:
    def __init__(self, environment: Environment):
        self.environment = environment
        self.state_names = {
            0 : "obstructed",
            1 : "free"
        }
        self.action_maps: dict[map, PathFinder] = {
            0: DijkstraM(self.environment),
            1: DepthDFS(self.environment),
            2: CarRandom(self.environment),
            3: Dijkstra(self.environment)
        }

        self.strategy = Strategy_Fsa(
            [
                [1 / len(self.action_maps) for _ in range(len(self.action_maps) )]
            ] * len(self.state_names),
            1
        )

        self.attempts: int = 0
        self.max_attempts: int = 3

        self.history_pos = []
        self.history_actions = []
        self.path = []

    def update(self, cur_pos: tuple[int, int], goal: tuple[int, int]):
        self.history_pos.append(cur_pos)
        if len(self.history_actions) > 0 and len(self.path) > 0:
            if len(self.history_pos) > 2 and self.history_pos[-1] != self.history_pos[-2]:
                self.strategy.reward(self.strategy.c_state, self.history_actions[-1], 1)
            else:
                self.strategy.no_reward(self.strategy.c_state, self.history_actions[-1], 1)

        """
        Try to update path using the action.
        """
        if len(self.path) == 0:
            action = self.strategy.choose()
            self.history_actions.append(action)
            self.path = self.action_maps[action].algorithm(cur_pos, goal)
        
        if len(self.path) == 0:
            self.path = [cur_pos]

        if len(self.history_pos) > 100:
            self.history_pos.pop(0)

        if len(self.history_pos) > 3 and self.history_pos[-1] == self.history_pos[-2] == self.history_pos[-3]:
            self.strategy.change_state(0)
            
        if (len(self.history_pos) > 3 and len(set([self.history_pos[-1], self.history_pos[-2], self.history_pos[-3]])) == 3):
            self.strategy.change_state(1)

    def next_pos(self) -> tuple[int, int]:
        return self.path.pop(0)