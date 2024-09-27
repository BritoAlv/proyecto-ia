import random
from threading import Thread
from environment import Environment, RoadBlock, SidewalkBlock
from sim.Car import Car
from sim.Walker import Walker
from sim.Semaphore import Semaphore

class EventHandler:
    def __init__(self, environment : Environment) -> None:
        self.environment = environment
        
    def _get_free_blocks(self, block_type : type):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])
        free_blocks : list[RoadBlock] = []

        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, block_type):
                    if block_type == RoadBlock and block.car_id == None:
                        free_blocks.append(block)
                    elif block_type == SidewalkBlock and block.walker_id == None:
                        free_blocks.append(block)
        return free_blocks
    
    def _get_type_blocks(self, block_type : type):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        blocks : list[block_type] = []
        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, block_type):
                    blocks.append(block)
        return blocks

