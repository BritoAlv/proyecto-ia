from environment import RoadBlock
from globals import Directions
from sim.Agent import Agent


import random
import time


class Semaphore(Agent):
    def act(self) -> None:
        while True:
            time.sleep(1)
            with self.environment.lock:
                light_directions = [
                    Directions.NORTH,
                    Directions.SOUTH,
                    Directions.EAST,
                    Directions.WEST
                ]

                self.environment.semaphores[self.id] = random.choice(light_directions)
        