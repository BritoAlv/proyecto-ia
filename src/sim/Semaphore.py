from environment import Environment, RoadBlock
from globals import Directions
from sim.Agent import Agent

import random

light_directions = [
    Directions.NORTH,
    Directions.SOUTH,
    Directions.EAST,
    Directions.WEST,
]


class Semaphore(Agent):
    def __init__(self, id, environment: Environment, gui_label):
        super().__init__(id, environment, gui_label)
        self.overload = 1
        self.current : Directions = Directions.NORTH

    def act(self) -> None:
        self.current = random.choice(light_directions)
