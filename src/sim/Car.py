from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent

import random
import time
import heapq

class CarGraphNode:
    def __init__(
        self, pos: tuple[int, int], direction: Directions, parent : 'CarGraphNode' ) -> None:
        self.pos = pos
        self.direction = direction
        self.score = 0
        self.parent : None | 'CarGraphNode' = parent

    def __hash__(self) -> int:
        return self.pos.__hash__()

    def __eq__(self, value: object) -> bool:
        return isinstance(value, CarGraphNode) and self.pos == value.pos
    
    def __lt__(self, value : object) -> bool:
        return isinstance(value, CarGraphNode) and self.score < value.score


class Car(MovingAgent):
    def __init__(
        self, position: tuple[int, int], goal: tuple[int, int], environment: Environment
    ):
        super().__init__(position, environment)
        self.next_positions: list[tuple[int, int]] = []
        self.attempts: int = 0
        self.goal: tuple[int, int] = goal
        self.max_attempts = 3
        self.p = 1


    def depth_bound_search(self, depth = 4) -> list[tuple[int, int]]:
        """
        look up until a depth, and choose the best path, goal is minimize distance. 
        """
        x, y = self.goal
        start_node = CarGraphNode(
            self.goal, self.environment.matrix[x][y].direction, None
        )

        queue : list[CarGraphNode] = []
        heapq.heappush(queue, start_node)

        seen : dict[tuple[int, int], CarGraphNode] = {}
        seen[self.position] = start_node

        while queue:
            top = heapq.heappop(queue)
            for neighbour, _ in self.get_neighbours(top):
                neighbour_score = neighbour.parent.score + 1
                if neighbour.pos not in seen:
                    seen[neighbour.pos] = neighbour
                    neighbour.score = neighbour_score
                    heapq.heappush(queue, neighbour)
                elif neighbour_score < seen[neighbour.pos].score:
                    seen[neighbour.pos].parent = top
                    seen[neighbour.pos].score = neighbour_score

        best_path, score = [], 1e9+1
        def dfs(curr_path = [self.position], curr_score = 0):
            if curr_path[-1] not in seen:
                return
            if len(curr_path) == depth + 1:
                if curr_score + seen[curr_path[-1]].score < score:
                    score = curr_score
                    best_path = curr_path
                return
            else:
                for neigbour, edge_weight in self.get_neighbours(seen[curr_path[-1]]):
                    if neighbour.pos not in curr_path:
                        dfs( curr_path + [neigbour.pos], curr_score + edge_weight )

        dfs()
        return best_path
 
    def dijkstra(self) -> list[tuple[int, int]]:
        x, y = self.position
        start_node = CarGraphNode(
            self.position, self.environment.matrix[x][y].direction, None
        )

        queue : list[CarGraphNode] = []
        heapq.heappush(queue, start_node)

        seen : dict[tuple[int, int], CarGraphNode] = {}
        seen[self.position] = start_node

        connected = False

        while queue:
            top = heapq.heappop(queue)
            for neighbour, edge_weight in self.get_neighbours(top):
                neighbour_score = neighbour.parent.score + 1 + (edge_weight - 1) / (neighbour.parent.score + 1)
                if neighbour.pos not in seen:
                    seen[neighbour.pos] = neighbour
                    neighbour.score = neighbour_score
                    heapq.heappush(queue, neighbour)
                elif neighbour_score < seen[neighbour.pos].score:
                    seen[neighbour.pos].parent = top
                    seen[neighbour.pos].score = neighbour_score

            if top.pos == self.goal:
                connected = True
                break

        if connected:
            path = [self.goal]
            while path[-1] != self.position:
                path.append((seen[path[-1]]).parent.pos)
            path.reverse()
            return path[1:]

        return []

    def get_neighbours(self, car: CarGraphNode) -> list[tuple[CarGraphNode, float]]:
        result = []
        x, y = car.pos
        direction = DIRECTION_OFFSETS[car.direction]

        x += direction[0]
        y += direction[1]

        if self.check_valid(x, y, RoadBlock):
            result.append( 
                (
                    CarGraphNode((x, y), car.direction, car),  
                    1 if self.environment.matrix[x][y].car_id == None else 2 )
                ) 
            

        elif self.check_valid(x, y, SemaphoreBlock):
            semaphor = self.environment.semaphores[self.environment.matrix[x][y].representative]
            result = [
                (
                    CarGraphNode(z, self.environment.matrix[z[0]][z[1]].direction, car), 
                    semaphor.overload + (1 if self.environment.matrix[z[0]][z[1]].car_id != None else 0)
                )
                for z in self.semaphor_options(x, y, car.direction)
            ]

        return result

    def path_finder(self) -> list[tuple[int, int]]:
        return self.dijkstra()

    def check_free(self, i, j):
        return (
            isinstance(self.environment.matrix[i][j], RoadBlock)
            and self.environment.matrix[i][j].car_id == None
        )

    def set_car_pos(self, i, j, x, y, id):
        self.environment.matrix[i][j].car_id = None
        self.environment.matrix[x][y].car_id = id
        self.environment.cars[id] = self
        self.position = (x, y)

    def update_list(self):
        """
        If the car doesn't move after two attempts delete this strategy.
        """
        if self.attempts >= self.max_attempts:
            self.next_positions = []

        """
        With probability p update the list to use a new one.
        """
        if random.random() < self.p:
            self.next_positions = self.path_finder()

    def remove_car(self):
        i, j = self.position
        self.environment.matrix[i][j].car_id = None
        self.environment.cars.pop(self.id)

    def act(self) -> None:
        i, j = self.position
        
        if self.position == self.goal:  # car reached goal so done.
            self.remove_car()
            return
        offset = DIRECTION_OFFSETS[self.environment.matrix[i][j].direction]
        direction = self.environment.matrix[i][j].direction
        self.update_list()

        print(f"Logging Car #{self.gui_label}")
        print(f"Position is {i, j}")
        print(f"Goal is {self.goal}")
        print(f"Path is {self.next_positions}")

        if len(self.next_positions) > 0:
            # use top position for moving
            next_pos = self.next_positions[0]
            x = next_pos[0]
            y = next_pos[1]

            car_moved = False

            # Check if cell is free and its valid.
            if self.check_valid(x, y, RoadBlock) and self.check_free(x, y):
                # Case 1 : there is a semaphore from (i, j) to (x, y)
                sem_x = i + offset[0]
                sem_y = j + offset[1]
                if self.check_valid(sem_x, sem_y, SemaphoreBlock):
                    representative = self.environment.matrix[sem_x][sem_y].representative
                    if direction == self.environment.semaphores[representative].current:
                        if next_pos in self.semaphor_options(sem_x, sem_y, direction):
                            self.set_car_pos(i, j, next_pos[0], next_pos[1], self.id)
                            car_moved = True
                # Case 2: (i, j) to (x, y)
                else:
                    if x - i == offset[0] and y - j == offset[1]:
                        self.set_car_pos(i, j, x, y, self.id)
                        car_moved = True

            if not car_moved:
                self.attempts += 1
            else:
                self.next_positions.pop(0)
        else:
            # use random moving to obtain next position
            m = offset[0]
            n = offset[1]
            x = i + m
            y = j + n
            if self.check_valid(x, y, RoadBlock):
                if self.check_free(x, y):
                    self.set_car_pos(i, j, x, y, self.id)
            elif self.check_valid(x, y, SemaphoreBlock):
                representative = self.environment.matrix[x][y].representative
                if direction == self.environment.semaphores[representative].current:
                    new_pos = self.pos_cross_semaphor(x, y, direction)
                    if self.check_free(new_pos[0], new_pos[1]):
                        self.set_car_pos(i, j, new_pos[0], new_pos[1], self.id)

    def pos_cross_semaphor(self, i, j, direction) -> tuple[int, int]:
        r = i
        c = j
        options = [(i, j)] + self.semaphor_options(r, c, direction)
        return options[random.randint(0, len(options) - 1)]

    def check_valid(self, x, y, class_instance):
        return valid_coordinates(
            x, y, len(self.environment.matrix), len(self.environment.matrix[0])
        ) and isinstance(self.environment.matrix[x][y], class_instance)

    def check_option(self, r, c, offset) -> list[tuple[int, int]]:
        options = []
        dx = offset[0]
        dy = offset[1]
        rr = r + dx
        cc = c + dy

        while self.check_valid(rr, cc, SemaphoreBlock):
            rr += dx
            cc += dy

        if self.check_valid(rr, cc, RoadBlock):
            if DIRECTION_OFFSETS[self.environment.matrix[rr][cc].direction] == offset:
                options.append((rr, cc))
        return options

    def semaphor_options(
        self, r: int, c: int, direction: Directions
    ) -> list[tuple[int, int]]:
        options = []
        while self.check_valid(r, c, SemaphoreBlock):
            if direction == Directions.NORTH or direction == Directions.SOUTH:
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.EAST])
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.WEST])
                if direction == Directions.NORTH:
                    r -= 1
                if direction == Directions.SOUTH:
                    r += 1
            else:
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.NORTH])
                options += self.check_option(r, c, DIRECTION_OFFSETS[Directions.SOUTH])
                if direction == Directions.EAST:
                    c -= 1
                if direction == Directions.WEST:
                    c += 1

        if self.check_valid(r, c, RoadBlock):
            options.append((r, c))

        return options