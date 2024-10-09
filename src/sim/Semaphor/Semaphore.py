import random
from environment import Environment
from globals import Directions
from sim.Agent import Agent
from sim.Semaphor.SemaphorLogic import SemaphorLogic
from sim.Semaphor.FuzzySemaphoreSystem import CAR_PROB, CAR_WAITING_TIME, MONTH, OVERLOAD, TIME_CLASSIFICATION, WALKER_WAITING_TIME, WHEATHER, build_fuzzySys

class Semaphore(Agent):
    def __init__(self, id, environment: Environment, gui_label : int, useFuzzy : bool = True ) :
        super().__init__(id, environment, gui_label)
        self.logic : SemaphorLogic = SemaphorLogic([])
        self.overload = 1
        self.fuzzy_values = {
            MONTH : 10, 
            TIME_CLASSIFICATION  : 450 , 
            WHEATHER: 0.5, 
            CAR_WAITING_TIME: 10, 
            WALKER_WAITING_TIME: 20
        }
        self.fuzzy_system = build_fuzzySys()
        
        self.car_times : list[int] = []
        self.walkers_times : list[int] = []
        self.useFuzzy = useFuzzy

    def add_direction(self, direction : Directions):
        self.logic.add_direction(direction)

    def update_system(self):
        if self.useFuzzy:
            result = self.fuzzy_system.process(self.fuzzy_values)
            self.logic.add_prob(result[CAR_PROB])
            self.overload = result[OVERLOAD]

    def update_input_vars(self):
        self.update_fuzzy( MONTH , self.environment.date.month)
        self.update_fuzzy( WHEATHER, self.environment.weather)
        self.update_fuzzy( TIME_CLASSIFICATION , self.environment.date.hour * 60 + self.environment.date.minute)

        if len(self.car_times) >= 3:
            sum = 0
            for x in self.car_times:
                sum += x
            avg_time = sum / len(self.car_times)
            self.update_fuzzy(CAR_WAITING_TIME, avg_time)
            self.car_times = []

        if len(self.walkers_times) >= 3:
            sum = 0
            for x in self.walkers_times:
                sum += x
            avg_time = sum / len(self.walkers_times)
            self.update_fuzzy(WALKER_WAITING_TIME, avg_time)
            self.walkers_times = []

    def get_current(self):
        return self.logic.current

    def update_fuzzy(self, name : str, value : float):
        self.fuzzy_values[name] = value

    def row_rem(self) -> int:
        """
        return the remaining time that the semaphor will follow
        """
        return self.logic.red_rem()

    def act(self) -> None:
        if self.logic.total_iter % 30 == 0:
            self.update_system()
        self.update_input_vars()
        self.logic.behaviour()