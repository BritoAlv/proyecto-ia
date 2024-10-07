from environment import Environment, PlaceBlock, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, valid_coordinates

from sim.MovingAgent import MovingAgent
from sim.Walker.WalkerDijkstra import WalkerDijkstra
from sim.Walker.WalkerRandom import WalkerRandom
from sim.Walker.PathFinder import PathFinder
from sim.Walker.PlaceBelief import PlaceBelief


import random

from sim.Walker.WalkerRandom import WalkerRandom

class Walker(MovingAgent):
    def __init__(self, environment: Environment):
        position = random.choice(environment.sidewalk_blocks).coordinates
        gui_label = len(environment.walkers)
        super().__init__(position, environment, gui_label)
        
        i, j = self.position
        self.environment.matrix[i][j].walkers_id.append(self.id)
        self.environment.walkers[self.id] = self

        self.path = []

        places = random.choices(self.environment.place_blocks, k=random.randint(1, len(self.environment.place_blocks)))
        places_g = random.choices(places, k=random.randint(1, len(places)))
        beliefs : dict[str, PlaceBelief] = {}
        place_desires : dict[str, int] = {}
        for place in places_g:
            place_desires[place.name] = 1
        for place in places:
            beliefs[place.name] = PlaceBelief(place.name, random.choice(self.environment.place_blocks).coordinates)

        self.place_beliefs = beliefs
        self.place_desires : dict[str, int] = place_desires
        
        # probs.
        self.social_prob = random.random()
        self.trust_ness = random.random()
        self.reactive_ness = random.random()
        self.reset_prob = 0.05

        # time for stats
        self.total_time_overall = 0
        self.semaphor_time_over_all = 0
        self.semaphor_stuck = 0
        self.semaphor_pos = None


    def remove_walker(self):
        i, j = self.position
        self.environment.matrix[i][j].walkers_id.remove(self.id)
        self.environment.walkers.pop(self.id)
        self.environment.stats.walkers_delay.append(self.total_time_overall)
        self.environment.stats.walkers_semaphore_delay.append(self.semaphor_time_over_all)

    def set_walker_pos(self, new: tuple[int, int]):
        i, j = self.position
        x, y = new
        assert(abs(i-x)+ abs(j -y) in [1, 0])
        current_block = self.environment.matrix[i][j]
        next_block = self.environment.matrix[x][y]
        self.position = (x, y)
        current_block.walkers_id.remove(self.id)
        next_block.walkers_id.append(self.id)

        if self.semaphor_pos != None:
            self.environment.semaphores[self.semaphor_pos].walkers_times.append(self.semaphor_stuck)
            self.semaphor_time_over_all += self.semaphor_stuck
            self.semaphor_stuck = 0
            self.semaphor_pos = None

    def try_move(self, next_pos : tuple[int, int]) -> bool:
        x, y = next_pos
        i, j = self.position
        matrix = self.environment.matrix
        next_block = matrix[x][y]
        cur_block = matrix[i][j]
        if isinstance(next_block, SidewalkBlock):
            self.set_walker_pos(next_pos)
            return True
        
        if isinstance(next_block, RoadBlock) and isinstance(cur_block, RoadBlock):
            self.set_walker_pos(next_pos)
            return True

        elif isinstance(next_block, RoadBlock):
            streets : list[tuple[int, int]] = []
            for i in range(len(self.path)):
                x, y = self.path[i]
                if isinstance(matrix[x][y], RoadBlock):
                    streets.append((x, y))
                elif isinstance(matrix[x][y], SidewalkBlock):
                    break

            works = True
            if isinstance(matrix[x][y], SidewalkBlock):
                for index, st  in enumerate(streets):
                    current_block = matrix[st[0]][st[1]]
                    p, q = DIRECTION_OFFSETS[current_block.direction]
                    sem_x = st[0] + p
                    sem_y = st[1] + q
                    if not valid_coordinates(sem_x, sem_y, len(matrix), len(matrix[0])) or not isinstance(matrix[sem_x][sem_y], SemaphoreBlock):
                        works = False
                        break
                    semaphore = self.environment.semaphores[matrix[sem_x][sem_y].representative]
                    if semaphore.current == current_block.direction or semaphore.time_till_change() < index + 1:
                        works = False
                        break
                if works:
                    self.semaphor_pos = matrix[sem_x][sem_y].representative
                    self.set_walker_pos(next_pos)
                    return True
        return False

    def update_beliefs(self):
        """
        1 - check if in position there is a neighbouring Intersest Place, if so updated my current info,
        2 - check if in position there is another walker and :
            - if social allows add to my knowledge its knowledge,
        """
        i, j = self.position
        for dx, dy in DIRECTION_OFFSETS.values():
            x = i + dx
            y = j + dy
            if valid_coordinates(x, y, len(self.environment.matrix), len(self.environment.matrix[0])):
                place = self.environment.matrix[x][y]
                if isinstance(place, PlaceBlock):
                    name = place.name
                    if name not in self.place_beliefs:
                        self.place_beliefs[name] = PlaceBelief(name, place.coordinates)

                    self.place_beliefs[name].belief_state = 1
                    self.place_beliefs[name].belief_pos = (x, y)

                    for place_name in self.place_beliefs:
                        place_coord = self.place_beliefs[place_name].belief_pos
                        if place_coord == (x, y) and name != place_name:
                            self.place_beliefs[place_name].belief_pos = random.choice(self.environment.place_blocks).coordinates

        for walker_id in self.environment.matrix[i][j].walkers_id:
            if walker_id != self.id and random.random() >= self.social_prob:
                other_walker = self.environment.walkers[walker_id]
                self.mix_beliefs(other_walker)

    def mix_beliefs(self, other : 'Walker'):
        others = other.place_beliefs
        for place_name in others:
            other_place_belief = others[place_name]
            if other_place_belief.belief_state == 1 or self.trust_ness <= 0.3:
                self.place_beliefs[place_name] = other_place_belief

    def update_desires(self):
        """
        Desires is a dict which contain a list of places and the desire to go to that place.
        The desire is a int >= 1.
        
        Option 1: there is a walker in my position that also wants to go to that place.
        Option 2: I know the location of the place.
        Option 3: Randomly I want to go to that place.
        Option 4: If I'm in a Place after some time I should not want to go to this place, so I decrease the desire.
        """

        self.update_desires_neigbours()
        self.update_desires_known_places()
        self.update_desires_reset()

    def update_desires_neigbours(self):
        i, j = self.position
        for walker_id in self.environment.matrix[i][j].walkers_id:
            if walker_id != self.id and random.random() >= self.social_prob:
                other_walker = self.environment.walkers[walker_id]
                for place_name in other_walker.place_desires:
                    if place_name in self.place_desires and self.place_beliefs[place_name].belief_state == 1:
                        self.place_desires[place_name] += 2

    def update_desires_known_places(self):
        for place_name in self.place_desires:
            if self.place_beliefs[place_name].belief_state == 1:
                self.place_desires[place_name] += 2

    def update_desires_reset(self):
        if random.random() <= self.reset_prob:
            for place_name in self.place_desires:
                self.place_desires[place_name] = 1

    def choose_intention(self):
        max_desire = max(self.place_desires.values())
        candidates = [place for place, desire in self.place_desires.items() if desire == max_desire]
        return random.choice(candidates)

    def choose_plan(self, place_intented : str) -> PathFinder:
        """
        This method should choose a method to compute the algorithm used to get to the path
        """
        """
        Implementation is : If desire is big enough and know where it is use dikstra, else use 
        a random to explore the environment.
        """
        if place_intented in self.place_desires and self.place_desires[place_intented] > 4 and self.place_beliefs[place_intented].belief_state == 1:
            return WalkerDijkstra(self.environment) # replace with Dikstra
        return WalkerRandom(self.environment)

    def check_done(self) -> bool:
        for place in self.place_desires:
            if self.place_beliefs[place].belief_state == 0:
                return False
        return True

    def act(self) -> None:
        # always update its beliefs
        self.update_beliefs()
        # if done then retire. 
        if self.check_done():
            self.remove_walker()
            return

        self.total_time_overall += 1

        i, j = self.position
        current_block = self.environment.matrix[i][j]
        # if there is no plan or wants to reconsider then:
        if not isinstance(current_block, RoadBlock) and (len(self.path) == 0 or random.random() <= self.reactive_ness):
            # update desires
            self.update_desires()
            # choose the intention with more desire        
            place_intention = self.choose_intention()
            # choose a plan to execute it, like Dikstra or random moving, etc.
            plan = self.choose_plan(place_intention)
            # the plan gives a path that the walker should follow.

            # a new path should set this to 0.
            self.semaphor_stuck = 0

            goal_place_pos = self.place_beliefs[place_intention].belief_pos
            for dx, dy in DIRECTION_OFFSETS.values():
                x = goal_place_pos[0] + dx
                y = goal_place_pos[1] + dy
                if valid_coordinates(x, y, len(self.environment.matrix), len(self.environment.matrix[0])):
                    if isinstance(self.environment.matrix[x][y], SidewalkBlock):
                        self.path = plan.path_finder(self.position, goal_place_pos)
                        assert(len(self.path) > 0)
                        break
        if len(self.path) > 0:
            next_pos = self.path[0]
            if self.try_move(next_pos):
                self.path.pop(0)
            else:
                self.semaphor_stuck += 1