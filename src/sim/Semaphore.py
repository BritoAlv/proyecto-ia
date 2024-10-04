from environment import Environment
from fuzzy.bounded_function import BoundedFunction
from fuzzy.fuzzy_system import FuzzySystem
from fuzzy.fuzzy_variable import FuzzyVariable
from globals import Directions
from sim.Agent import Agent

light_directions = [
    Directions.NORTH,
    Directions.SOUTH,
    Directions.EAST,
    Directions.WEST,
]

WHEATHER = "Wheather"
RAINING = "raining"
CLOUD = "cloud"
SUNNY = "sunny"

CAR_WAITING_TIME = "Car Waiting Time"
WALKER_WAITING_TIME = "Walker Waiting Time"

NORMAL = "normal"
CHARGED = "charged"
OVERCHARGED = "overcharged"


OVERLOAD = "Overload"
LOW = "Low"
AVERAGE = "average"
HIGH = "High"

GREEN_TIME = "Green Time"

wheather = FuzzyVariable(WHEATHER, 0, 10, {RAINING: BoundedFunction.gaussian_function(1, 0, 2, 0, 10), CLOUD: BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10), SUNNY: BoundedFunction.gaussian_function(1, 10, 2, 0, 10)})

car_wait_time = FuzzyVariable(CAR_WAITING_TIME, 0, 100, {NORMAL: BoundedFunction.gaussian_function(1, 0, 10, 0, 100), CHARGED: BoundedFunction.gaussian_function(1, 40, 10, 0, 100), OVERCHARGED: BoundedFunction.gaussian_function(1, 100, 20, 0, 100)})

walker_wait_time = FuzzyVariable(WALKER_WAITING_TIME, 0, 100, {NORMAL: BoundedFunction.gaussian_function(1, 0, 10, 0, 100), CHARGED: BoundedFunction.gaussian_function(1, 40, 10, 0, 100), OVERCHARGED: BoundedFunction.gaussian_function(1, 100, 20, 0, 100)})

DAWN = "dawn"
MORNING = "morning"
AFTERNOON = "afternoon"
NOON = "noon"

time_classification = {
    DAWN : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0 , 180, 1),
            BoundedFunction.linear_interpolate(180, 1, 420, 0),
            BoundedFunction.linear_interpolate(420, 0, 1440, 0)
        ]
    ),
    MORNING : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 360, 0),
            BoundedFunction.linear_interpolate(360, 0, 600, 1),
            BoundedFunction.linear_interpolate(600, 1, 780, 0),
            BoundedFunction.linear_interpolate(780, 0, 1440, 0)
        ]
    ),
    AFTERNOON : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 720, 0),
            BoundedFunction.linear_interpolate(720, 0, 960, 1),
            BoundedFunction.linear_interpolate(960, 1, 1200, 0),
            BoundedFunction.linear_interpolate(1200, 0, 1440, 0),

        ]
    ),
    NOON: BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0.2, 60, 0),
            BoundedFunction.linear_interpolate(60, 0, 1140, 0),
            BoundedFunction.linear_interpolate(1140, 0, 1320, 1),
            BoundedFunction.linear_interpolate(1320, 1, 1440, 0.2),
        ]
    )
}

TIME_CLASSIFICATION = "Time Classification" # ranges from 0 to 1440, the simulation should hold this as time.
time_var = FuzzyVariable( TIME_CLASSIFICATION, 0, 1440, time_classification)



green_time = FuzzyVariable(GREEN_TIME, 1, 10, {
    LOW : BoundedFunction.gaussian_function(1, 1, 2, 1, 10),
    AVERAGE : BoundedFunction.gaussian_function(1, 4, 1.5, 1, 10),
    HIGH : BoundedFunction.gaussian_function(1, 10, 2, 1, 10),
})

overload = FuzzyVariable(
    OVERLOAD,
    0,
    10,
    {
        LOW: BoundedFunction.gaussian_function(1, 0, 2, 0, 10),
        AVERAGE: BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
        HIGH: BoundedFunction.gaussian_function(1, 10, 2, 0, 10),
    },
)

class Semaphore(Agent):
    def __init__(self, id, environment: Environment, gui_label):
        super().__init__(id, environment, gui_label)
        self.directions = [Directions.EMPTY]
        self.overload = 1
        self.green_time = 4
        self.iter = 0
        self.index = 0
        self.current: Directions = Directions.NORTH
        self.fuzzy_values = {TIME_CLASSIFICATION  : 450 , WHEATHER: 5, CAR_WAITING_TIME: 50, WALKER_WAITING_TIME: 50}
        self.fuzzy_system = FuzzySystem(input_f=[time_var, wheather, car_wait_time, walker_wait_time], output_f=[green_time, overload])
        self.queue = []
        
        self.fuzzy_system.add_rule(GREEN_TIME, LOW, lambda x: min(x[CAR_WAITING_TIME][NORMAL], x[WALKER_WAITING_TIME][NORMAL], 1 - x[WHEATHER][RAINING], x[TIME_CLASSIFICATION][DAWN], x[TIME_CLASSIFICATION][NOON]))
        self.fuzzy_system.add_rule(GREEN_TIME, AVERAGE, lambda x: min(x[CAR_WAITING_TIME][CHARGED], x[WALKER_WAITING_TIME][CHARGED], 1 - x[WHEATHER][CLOUD], x[TIME_CLASSIFICATION][MORNING]))
        self.fuzzy_system.add_rule(GREEN_TIME, HIGH, lambda x: max(x[CAR_WAITING_TIME][OVERCHARGED], x[WALKER_WAITING_TIME][OVERCHARGED], 1 - x[WHEATHER][SUNNY], x[TIME_CLASSIFICATION][AFTERNOON]))
        self.fuzzy_system.add_rule(OVERLOAD, LOW, lambda x: max(x[CAR_WAITING_TIME][NORMAL], x[WALKER_WAITING_TIME][NORMAL]))
        self.fuzzy_system.add_rule(OVERLOAD, AVERAGE, lambda x: max(x[CAR_WAITING_TIME][CHARGED], x[WALKER_WAITING_TIME][CHARGED]))
        self.fuzzy_system.add_rule(OVERLOAD, HIGH, lambda x: max(x[CAR_WAITING_TIME][OVERCHARGED], x[WALKER_WAITING_TIME][OVERCHARGED]))

    def add_direction(self, direction : Directions):
        if direction not in self.directions:
            self.directions.append(direction)

    def update_system(self):
        result = self.fuzzy_system.process(self.fuzzy_values)
        self.queue.append(result[GREEN_TIME])
        self.overload = result[OVERLOAD]

    def update_fuzzy(self, name : str, value : float):
        self.fuzzy_values[name] = value

    def time_till_change(self) -> int:
        """
        return the remaining time that the semaphor will follow
        """
        return self.green_time - self.iter - 1

    def act(self) -> None:
        """
        The semaphor has a green time for default, this is updated using the fuzzy logic, the fuzzy values are updated using the set_fuzzy_values method. the semaphor will keep on a state until the green time is over, then it will change to the next direction in the array, if the direction is empty it will be red on all the directions, else will be green on a specific direction.
        """
        if self.iter >= self.green_time:
            if len(self.queue) > 0:
                self.green_time = self.queue.pop()
            self.iter = 0
            self.index += 1
            self.index %= len(self.directions)
        
        self.iter += 1
        self.current = self.directions[self.index]