import pickle
import sys
from threading import Thread
import time
from uuid import UUID
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QFont

from environment import Environment, PlaceBlock, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent
from sim.event_handler import EventHandler
from ui.start_window import StartWindow


class ZoomableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.zoom_factor = 1.15

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:  # Scroll up (zoom in)
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Scroll down (zoom out)
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)


class SemaphoreItem:
    def __init__(self) -> None:
        self.light_directions : dict[int, QGraphicsItem] = {}

class SimulationWindow(QWidget):
    def __init__(self, matrix_path : str):
        super().__init__()

        # Load matrix data into main memory
        with open(matrix_path, 'rb') as file:
            matrix = pickle.load(file)
        environment = Environment(matrix)

        # Business (simulation) logic properties
        self._environment = environment # Core data structure

        ## Properties to display agents
        self._car_items : dict[UUID, QGraphicsItem] = {}
        self._walker_items : dict[UUID, QGraphicsItem] = {}
        self._semaphore_items : dict[tuple[int, int], SemaphoreItem] = {}

        self._home_window : StartWindow = None # Reference to window
        self._scale_factor = 60 ## Scale factor to visualize items

        ## Properties to display labels
        self._cars = {}
        self._agent_labels = {}

        # Create and connect timer to handle the simulation loop
        self.timer = QTimer()
        self.timer.timeout.connect(self._simulate)

        # Visualization setup
        self.setWindowTitle("Simulation")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)

        ## Add a horizontal top-layout to hold control buttons
        top_layout = QHBoxLayout()

        ### Setup control buttons
        start_button = QPushButton("Start")
        start_button.setFixedSize(200, 30)
        stop_button = QPushButton("Stop")
        stop_button.setFixedSize(200, 30)
        end_button = QPushButton("End and see results")
        end_button.setFixedSize(200, 30)

        start_button.clicked.connect(self._handle_start)
        stop_button.clicked.connect(self._handle_stop)
        end_button.clicked.connect(self._handle_end)

        top_layout.addWidget(start_button)
        top_layout.addWidget(stop_button)
        top_layout.addWidget(end_button)

        main_layout.addLayout(top_layout)

        ## Add view and simulation scene to visualize the actual map with all events
        self.view = ZoomableGraphicsView()
        self.simulation_scene = QGraphicsScene()
        self._build_simulation_scene()
        self.view.setScene(self.simulation_scene)

        main_layout.addWidget(self.view)
        self.setLayout(main_layout)

    def _simulate(self):
        '''
        Core simulation method, it holds an iteration over the simulation loop
        '''
        # Convert dictionary values to list (in three cases) to avoid dictionary overwriting while iterating
        for semaphore in list(self._environment.semaphores.values()):
                semaphore.act()

        for car in list(self._environment.cars.values()):
            car.act()
        
        for walker in list(self._environment.walkers.values()):
            walker.act()

        self._update_scene()

    def _handle_start(self):
        self.timer.start(100)

    def _handle_stop(self):
        self.timer.stop()

    def _handle_end(self):
        self.timer.stop()
        self._home_window = StartWindow()
        self._home_window.showMaximized()

        self.close()

    def _build_simulation_scene(self):
        matrix = self._environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        # Set background
        background = QGraphicsRectItem(0, 0, width * self._scale_factor, height * self._scale_factor)
        background.setBrush(QBrush(Qt.darkGreen))
        self.simulation_scene.addItem(background)

        for i in range(height):
            for j in range(width):
                block = matrix[i][j]
                if isinstance(block, SidewalkBlock):
                    color = Qt.yellow
                elif isinstance(block, RoadBlock):
                    color = Qt.lightGray
                elif isinstance(block, SemaphoreBlock):
                    color = Qt.darkGray
                elif isinstance(block, PlaceBlock):
                    color = Qt.white
                else:
                    continue

                rectangle = self._add_rectangle(i, j, self._scale_factor, self._scale_factor, color)

                if isinstance(block, RoadBlock):
                    pos = f" ({i}, {j})"
                    if block.direction == Directions.NORTH:
                        self._add_text('N'+ pos, i, j)
                    elif block.direction == Directions.SOUTH:
                        self._add_text('S'+ pos, i, j)
                    elif block.direction == Directions.EAST:
                        self._add_text('E'+ pos, i, j)
                    elif block.direction == Directions.WEST:
                        self._add_text('W' + pos, i, j)

                # Create semaphore_items
                if isinstance(block, RoadBlock):
                    p, q = DIRECTION_OFFSETS[block.direction]
                    if not valid_coordinates(i + p, j + q, height, width):
                        continue
                    neighbor = matrix[i + p][j + q]
                    if isinstance(neighbor, SemaphoreBlock):
                        representative = neighbor.representative
                        if representative not in self._semaphore_items:
                            self._semaphore_items[representative] = SemaphoreItem()
                        self._semaphore_items[representative].light_directions[block.direction] = rectangle

    def _add_rectangle(self, i : int, j : int, width : int, height : int, color : Qt.BrushStyle) -> QGraphicsRectItem:
        x = j * self._scale_factor
        y = i * self._scale_factor

        rectangle = QGraphicsRectItem(x, y, width, height)
        rectangle.setBrush(QBrush(color))
        rectangle.__setattr__('absolute_position', (x, y)) # This is not good practice
        self.simulation_scene.addItem(rectangle)
        return rectangle
    
    def __add_text__(self, text : str, x : float, y : float):
        text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 8, QFont.Thin)
        text_item.setFont(font)
        text_item.setPos(x, y)
        self.simulation_scene.addItem(text_item)
        return text_item


    def _add_text(self, text : str, i : int, j : int):
        return self.__add_text__(text, j * self._scale_factor, i * self._scale_factor)
        
    
    def _update_scene(self):
        self._change_lights()
        self._move_agent(self._environment.cars, self._car_items)
        self._move_agent(self._environment.walkers, self._walker_items, Qt.cyan, 15)

    def _change_lights(self):
        for semaphore_id in self._environment.semaphores:
            light_direction = self._environment.semaphores[semaphore_id].current
            
            semaphore_item = self._semaphore_items[semaphore_id]
            for direction in semaphore_item.light_directions:
                if direction == light_direction:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.green))
                else:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.red))

    def _move_agent(self, environment_agents : dict[UUID, MovingAgent], scene_items : dict[UUID, QGraphicsItem], color : Qt.BrushStyle = Qt.blue, agent_size : int = 30):
        # Add new agent and update existing ones
        for agent_id in environment_agents:
            i, j = environment_agents[agent_id].position
            if agent_id not in scene_items:
                agent_item = self._add_rectangle(i, j, agent_size, agent_size, color)
                self._agent_labels[agent_id] = self.__add_text__(str(environment_agents[agent_id].gui_label), agent_item.x(), agent_item.y())
                scene_items[agent_id] = agent_item
            else:
                agent_item = scene_items[agent_id]
                x_previous, y_previous = agent_item.absolute_position
                x, y = j * self._scale_factor, i * self._scale_factor

                scaled_offset = self._scale_factor / 3.5
                agent_item.setX(x - x_previous + scaled_offset)
                agent_item.setY(y - y_previous + scaled_offset)
                self._agent_labels[agent_id].setPos(x + scaled_offset, y + scaled_offset)
                agent_item.update()
                
        # Remove unused agents
        items_to_drop = []
        for item_id in scene_items:
            if item_id not in environment_agents:
                items_to_drop.append(item_id)
        
        for item_id in items_to_drop:
            self.simulation_scene.removeItem(scene_items[item_id])
            scene_items.pop(item_id)
            self.simulation_scene.removeItem(self._agent_labels[item_id])
            self._agent_labels.pop(item_id)

if __name__ == '__main__':  
    app = QApplication(sys.argv)
    window = SimulationWindow("./src/ui/matrices/matrix.pkl")
    window.showMaximized()
    app.exec_()