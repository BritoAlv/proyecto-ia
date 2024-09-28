import heapq
from environment import Environment, RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarGraphNode import CarGraphNode, PathFinder
from sim.Car.CarCommon import check_valid, semaphor_options

INF = 1e9+1

class DepthDFS(PathFinder):
    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self.best_path = []
        self.score = INF
    def algorithm(self, cur_pos: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        self.best_path = []
        self.score = INF
        self.depth_bound_search(cur_pos, goal)
        if len(self.best_path) > 0:
            return self.best_path[1:]
        else:
            return []

    def get_neighbours(self, current: CarGraphNode) -> list[(CarGraphNode, float)]:
        """
        Implementation Details ( w = weight of edge ):
            - edge A -> B, where B is road : 
                if B contains car, w = 2, else w = 1
            - edge A -> B, where B implies cross a semaphor :
                w = semaphore.overload + (1 if car else 0)
        """
        result = []
        x, y = current.pos
        direction = DIRECTION_OFFSETS[current.direction]

        x += direction[0]
        y += direction[1]

        if check_valid(x, y, RoadBlock, self.environment):
            additional_weight = 1 if self.environment.matrix[x][y].car_id == None else 2
            additional_weight /= 10
            result.append( 
                (
                    CarGraphNode((x, y), current.direction, current), additional_weight)
                ) 
            
        elif check_valid(x, y, SemaphoreBlock, self.environment):
            semaphor = self.environment.semaphores[self.environment.matrix[x][y].representative]
            result = [
                (
                    CarGraphNode(z, self.environment.matrix[z[0]][z[1]].direction, current), 
                    (semaphor.overload + (1 if self.environment.matrix[z[0]][z[1]].car_id != None else 0) / 10 )
                )
                for z in semaphor_options(x, y, current.direction, self.environment)
            ]
        return result

    
    def depth_bound_search(self, cur_pos : tuple[int, int],  goal : tuple[int, int], depth = 4):
        """
        look up until a depth, and choose the best path, goal is minimize distance in effor to minimize traffic. 
        """
        
        def bfs(cur_pos : tuple[int, int], goal : tuple[int, int]):
            x, y = cur_pos
            start_node = CarGraphNode(
                cur_pos, self.environment.matrix[x][y].direction, None
            )

            queue : list[CarGraphNode] = []
            heapq.heappush(queue, start_node)

            seen : dict[tuple[int, int], CarGraphNode] = {}
            seen[cur_pos] = start_node
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
                
                if top.pos == goal:
                    return top.score
            return INF 

        def dfs(curr_path = [cur_pos], curr_score = 0):
            if goal in curr_path:
                self.score = 0
                self.best_path = curr_path
            if len(curr_path) == depth + 1:
                to_goal_distance = bfs(curr_path[-1], goal)
                if to_goal_distance != INF:
                    if curr_score + to_goal_distance < self.score:
                        self.score = curr_score
                        self.best_path = curr_path
            else:
                x, y = curr_path[-1]
                for neigbour, edge_weight in self.get_neighbours(CarGraphNode(curr_path[-1], self.environment.matrix[x][y].direction,None)):
                    if neigbour.pos not in curr_path:
                        dfs( curr_path + [neigbour.pos], curr_score + edge_weight )
        dfs()