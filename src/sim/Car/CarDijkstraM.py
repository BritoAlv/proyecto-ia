import heapq
from environment import RoadBlock, SemaphoreBlock
from globals import DIRECTION_OFFSETS
from sim.Car.CarGraphNode import CarGraphNode, PathFinder
from sim.Car.CarCommon import check_valid, semaphor_options


class DijkstraM(PathFinder):
    def algorithm(self, cur_pos : tuple[int, int], goal : tuple[int, int]) -> list[tuple[int, int]]:
        return self.dijkstraM(cur_pos, goal)

    def get_neighbours(self, current : CarGraphNode) -> list[tuple[CarGraphNode, float]]:
        result = []
        x, y = current.pos
        direction = DIRECTION_OFFSETS[current.direction]

        x += direction[0]
        y += direction[1]

        if check_valid(x, y, RoadBlock, self.environment):
            result.append( 
                (
                    CarGraphNode((x, y), current.direction, current),  
                    1 if self.environment.matrix[x][y].car_id == None else 2 )
                ) 
            
        elif check_valid(x, y, SemaphoreBlock, self.environment):
            semaphor = self.environment.semaphores[self.environment.matrix[x][y].representative]
            result = [
                (
                    CarGraphNode(z, self.environment.matrix[z[0]][z[1]].direction, current), 
                    semaphor.overload + (1 if self.environment.matrix[z[0]][z[1]].car_id != None else 0)
                )
                for z in semaphor_options(x, y, current.direction, self.environment)
            ]
        return result

    def dijkstraM(self, cur_pos : tuple[int, int], goal : tuple[int, int]) -> list[tuple[int, int]]:
        x, y = cur_pos
        start_node = CarGraphNode(
            cur_pos, self.environment.matrix[x][y].direction, None
        )

        queue : list[CarGraphNode] = []
        heapq.heappush(queue, start_node)

        seen : dict[tuple[int, int], CarGraphNode] = {}
        seen[cur_pos] = start_node

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

            if top.pos == goal:
                connected = True
                break

        if connected:
            path = [goal]
            while path[-1] != cur_pos:
                path.append((seen[path[-1]]).parent.pos)
            path.reverse()
            return path[1:]

        return []