import pickle
import sys
from uuid import UUID
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QFont

from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.event_handler import EventHandler


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

class GraphicWindow(QWidget):
    def __init__(self, environment : Environment):
        super().__init__()

        self.scale_factor = 60
        self.environment = environment
        self.car_items : dict[UUID, QGraphicsItem] = {}
        self.walker_items : dict[UUID, QGraphicsItem] = {}
        self.semaphore_items : dict[tuple[int, int], SemaphoreItem] = {}

        # Set up the main layout (vertical layout for buttons and view)
        main_layout = QVBoxLayout()

        # Create a label to display some information
        self.label = QLabel("Traffic Simulation Control", self)
        main_layout.addWidget(self.label) 
        self.cars = {}
        self.agent_labels = {}

        # Create buttons for start, stop, etc.
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        self.view = ZoomableGraphicsView()
        self.simulation_scene = QGraphicsScene()
        self._build_simulation_scene()

        # Set the scene for the view
        self.view.setScene(self.simulation_scene)

        # Add the QGraphicsView to the main layout
        main_layout.addWidget(self.view)

        # Set the layout on the main widget
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_scene)
        self.timer.start(100)

    def _build_simulation_scene(self):
        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        # Set background
        background = QGraphicsRectItem(0, 0, width * self.scale_factor, height * self.scale_factor)
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
                else:
                    continue

                rectangle = self._add_rectangle(i, j, self.scale_factor, self.scale_factor, color)

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
                        if representative not in self.semaphore_items:
                            self.semaphore_items[representative] = SemaphoreItem()
                        self.semaphore_items[representative].light_directions[block.direction] = rectangle

    def _add_rectangle(self, i : int, j : int, width : int, height : int, color : Qt.BrushStyle) -> QGraphicsRectItem:
        x = j * self.scale_factor
        y = i * self.scale_factor

        rectangle = QGraphicsRectItem(x, y, width, height)
        rectangle.setBrush(QBrush(color))
        rectangle.__setattr__('absolute_position', (x, y)) # This is not good practice
        self.simulation_scene.addItem(rectangle)
        return rectangle
    
    def __add_text(self, text : str, x : float, y : float):
        text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 8, QFont.Thin)
        text_item.setFont(font)
        text_item.setPos(x, y)
        self.simulation_scene.addItem(text_item)
        return text_item


    def _add_text(self, text : str, i : int, j : int):
        return self.__add_text(text, j * self.scale_factor, i * self.scale_factor)
        
    
    def _update_scene(self):
        with self.environment.lock:
            self._change_lights()
            self._move_agent(self.environment.cars, self.car_items)
            self._move_agent(self.environment.walkers, self.walker_items, Qt.cyan, 15)

    def _change_lights(self):
        for semaphore_id in self.environment.semaphores:
            light_direction = self.environment.semaphores[semaphore_id]
            
            semaphore_item = self.semaphore_items[semaphore_id]
            for direction in semaphore_item.light_directions:
                if direction == light_direction:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.green))
                else:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.red))

    def _move_agent(self, environment_agents : dict[UUID, tuple[int, int]], scene_items : dict[UUID, QGraphicsItem], color : Qt.BrushStyle = Qt.blue, agent_size : int = 30):
        # Add new agent and update existing ones
        for agent_id in environment_agents:
            i, j = environment_agents[agent_id]
            if agent_id not in scene_items:
                agent_item = self._add_rectangle(i, j, agent_size, agent_size, color)
                self.agent_labels[agent_id] = self.__add_text(str(len(self.agent_labels)), agent_item.x(), agent_item.y())
                scene_items[agent_id] = agent_item
            else:
                agent_item = scene_items[agent_id]
                x_previous, y_previous = agent_item.absolute_position
                x, y = j * self.scale_factor, i * self.scale_factor

                scaled_offset = self.scale_factor / 3.5
                agent_item.setX(x - x_previous + scaled_offset)
                agent_item.setY(y - y_previous + scaled_offset)

                self.agent_labels[agent_id].setPos(x + scaled_offset, y + scaled_offset)
                

        # Remove unused agents
        items_to_drop = []
        for item_id in scene_items:
            if item_id not in environment_agents:
                items_to_drop.append(item_id)
        
        for item_id in items_to_drop:
            self.simulation_scene.removeItem(scene_items[item_id])
            scene_items.pop(item_id)
        
app = QApplication(sys.argv)

with open("./src/ui/matrices/matrix.pkl", 'rb') as file:
    matrix = pickle.load(file)
environment = Environment(matrix)
event_handler = EventHandler(environment)
        
window = GraphicWindow(environment)
window.show()
event_handler.start()

app.exec_()