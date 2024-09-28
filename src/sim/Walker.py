from environment import SidewalkBlock
from globals import valid_coordinates
from sim.MovingAgent import MovingAgent


import random

class Walker(MovingAgent):
    def act(self) -> None:
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        i, j = self.position
        current_block = matrix[i][j]
        
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
                self.environment.walkers[self.id] = self
                self.position = x, y
                break