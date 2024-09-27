from datetime import datetime, timedelta
from enum import Enum
import random
from numpy.random import exponential

from environment import Environment, RoadBlock, SidewalkBlock
from sim.Car import Car

class EventType(Enum):
    CAR_EVENT = 0
    WALKER_EVENT = 1

class Event: 
    def __init__(self, date: datetime, event_type : EventType) -> None:
        self.date = date
        self.type : EventType = event_type

    def __lt__(self, other) -> bool:
        if not isinstance(other, Event):
            raise Exception(f"Cannot apply < between an {type(self)} instance and a {type(other)} instance")
        return self.date < other.date
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Event):
            return False
        return self.date == value.date
    

class EventHandler:
    def __init__(self, environment : Environment) -> None:
        self.environment = environment

    def handle(self, event : Event) -> Event:
        if event.type == EventType.CAR_EVENT:
            return self._handle_car_event(event)
        elif event.type == EventType.WALKER_EVENT:
            return self._handle_walker_event(event)
    
    def _handle_car_event(self, event : Event) -> Event:
        # TODO: The exponential average time should vary depending on the time of the day (check on non-stationary Poisson Process to achieve accuracy)
        # Create a new Car-Event, using a Poisson distribution for car-event dates
        time_offset = exponential(300)
        next_date = event.date + timedelta(seconds=time_offset)
        next_car_event = Event(next_date, EventType.CAR_EVENT)

        # Get non-occupied road-blocks
        free_blocks = self._get_free_blocks(RoadBlock)

        # Create and set up a new car
        car = Car(random.choice(free_blocks).coordinates, random.choice(free_blocks).coordinates, self.environment)
        self.environment.cars[car.id] = car

        return next_car_event
    
    def _handle_walker_event(self, event : Event) -> Event:
        pass
        
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