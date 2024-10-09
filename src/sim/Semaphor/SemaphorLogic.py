from globals import Directions


class SemaphorLogic:
    def __init__(self, directions : list[Directions]):
        self.green_state = False
        self.directions = directions
        self.current : Directions = Directions.EMPTY
        self.prob_car = 0.60
        self.cycle_time = 7*(len(self.directions) +  (4 - len(self.directions) % 4))
        self.iter = 0
        self.queue : list[float] = []
        self.total_iter  = 0

    def add_direction(self, direction: Directions):
        if direction not in self.directions:
            self.directions.append(direction)

    def add_prob(self, prob : float):
        self.queue.append(prob)

    def car_time(self):
        return int(self.cycle_time * self.prob_car)
    
    def walker_time(self):
        return int(self.cycle_time * (1 - self.prob_car))

    def red_rem(self):
        return self.cycle_time - self.iter - 1

    def behaviour(self):
        self.iter += 1
        self.total_iter += 1
        self.total_iter %= 1001

        if len(self.directions) == 0:
            self.green_state = False
            self.iter = 0

        if self.green_state:
            if self.iter >= self.car_time():
                self.iter = 0
                self.green_state = not self.green_state
                self.current = Directions.EMPTY
                return
            
            number_directions = len(self.directions)
            for i in range(1, number_directions + 1):
                if self.iter <= (i * self.car_time()) / number_directions:
                    self.current = self.directions[i-1]
                    return
        else:
            if self.iter >= self.car_time():
                self.iter = 0
                self.green_state = not self.green_state
                self.current = self.directions[0]
                return