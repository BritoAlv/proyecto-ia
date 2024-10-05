from datetime import datetime, timedelta
from enum import Enum
import math
import random
import numpy as np
from numpy.random import exponential

from environment import Environment, RoadBlock, SidewalkBlock
from sim.Car.Car import Car

class EventType(Enum):
    CAR_EVENT = 0
    WALKER_EVENT = 1
    RAIN_EVENT = 2

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
        elif event.type == EventType.RAIN_EVENT:
            return self._handle_rain_event(event)
    
    def _handle_car_event(self, event : Event) -> Event:
        # TODO: The exponential average time should vary depending on the time of the day (check on non-stationary Poisson Process to achieve accuracy)
        # Create a new Car-Event, using a Poisson distribution for car-event dates
        time_offset = math.ceil(exponential(30))
        next_date = event.date + timedelta(seconds=time_offset)
        next_car_event = Event(next_date, EventType.CAR_EVENT)

        # Get non-occupied road-blocks
        free_blocks = self._get_free_blocks(RoadBlock)
        if len(free_blocks) > 0:
            goals, goals_probabilities = self._get_roads_probabilities()

            start_position = random.choice(free_blocks).coordinates
            goal_position = random.choices(goals, goals_probabilities)[0]

            # Create and set up a new car
            car = Car(start_position, goal_position, self.environment, len(self.environment.cars))
            self.environment.cars[car.id] = car

        return next_car_event
    
    def _handle_walker_event(self, event : Event) -> Event:
        pass

    def _handle_rain_event(self, event: Event) -> Event:
        wet_months = [5, 6, 7, 8, 9, 10, 11]
        mean = 1 if event.date.month in wet_months else 10
        time_offset = math.ceil(exponential(mean))
        next_date = event.date + timedelta(days=time_offset)
        next_rain_event = Event(next_date, EventType.RAIN_EVENT)

        mean = 0.9 if event.date.month in wet_months else 0.7
        standard_deviation = 0.1
        beta = mean / math.pow(standard_deviation, 2)
        alpha = mean * beta
        rain_intensity = random.gammavariate(alpha, 1 / beta)
        self.environment.weather = rain_intensity

        return next_rain_event
        
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
    
    def _get_type_blocks(self, block_type : type) -> list:
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
    
    def _get_roads_probabilities(self) -> tuple[list[tuple[int, int]], list[float]]:
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])
        places_probability : dict[tuple[int, int], float] = self._get_places_probability()

        roads : list[tuple[int, int]] = []
        probabilities : list[float] = []

        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, RoadBlock):
                    roads.append(block.coordinates)
                    if (i, j) in places_probability:
                        probabilities.append(places_probability[(i, j)])
                    else:
                        probabilities.append(self._get_road_probability((i, j), places_probability))
        
        return roads, probabilities

    
    def _get_places_probability(self, car_biased : bool = True) -> dict[tuple[int, int], float]:
        places_probabilities : dict[tuple[int, int], list[float]] = {}
        places_probability : dict[tuple[int, int], float] = {}
        
        for place in self.environment.places.values():
            # Process place
            probability = 0.9 # Template, actual method should use nlp to calculate that probability

            if place.representative not in places_probabilities:
                places_probabilities[place.representative] = [probability]
            else:
                places_probabilities[place.representative].append(probability)
        
        for place_representative in places_probabilities:
            places_probability[place_representative] = np.average(places_probabilities[place_representative])

        return places_probability
    
    
    def _get_manhattan_distance(self, coord1 : tuple[int, int], coord2 : tuple[int, int]):
        row1, col1 = coord1
        row2, col2 = coord2
        return abs(row1 - row2) + abs(col1 - col2)
    
    
    def _get_road_probability(self, road_coord : tuple[int, int], places_probability : dict[tuple[int, int], float]):
        if len(places_probability) == 0:
            return 0.5
        
        smallest_distance = 1e10
        closest_place_probability = 0
        for place_coord in places_probability:
            place_probability = places_probability[place_coord]

            distance = self._get_manhattan_distance(road_coord, place_coord)
            if distance < smallest_distance:
                smallest_distance = distance
                closest_place_probability = place_probability

        factor = 1 - 0.05 * smallest_distance if smallest_distance < 20 else 1 - 0.05 * 19

        return closest_place_probability * factor
 