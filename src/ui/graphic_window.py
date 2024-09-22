from math import ceil
import pickle
import sys
from uuid import UUID
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QBrush, QPolygonF

from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock
from ui.globals import Directions, valid_coordinates

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
        self.semaphore_items : dict[tuple[int, int], SemaphoreItem] = {}

        # Set up the main layout (vertical layout for buttons and view)
        main_layout = QVBoxLayout()

        # Create a label to display some information
        self.label = QLabel("Traffic Simulation Control", self)
        main_layout.addWidget(self.label)
        self.cars = {}

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

        direction_offsets = {
            Directions.NORTH: (-1, 0),
            Directions.SOUTH: (1, 0),
            Directions.EAST: (0, -1),
            Directions.WEST: (0, 1)
        }

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
                    p, q = direction_offsets[block.direction]
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
        self.simulation_scene.addItem(rectangle)
        return rectangle
    
    def _add_car(self, i : int, j : int, width : int, height : int, color : Qt.BrushStyle):
        x = j * self.scale_factor
        y = i * self.scale_factor

        # Define the triangle's vertices
        points = QPolygonF([
            QPointF(x, y),                   # Top vertex
            QPointF(x - width / 2, y + height),  # Bottom left vertex
            QPointF(x + width / 2, y + height)   # Bottom right vertex
        ])
        
        # Create the polygon item and set its brush color
        car = QGraphicsPolygonItem(points)
        car.setBrush(QBrush(color))
        car.__setattr__('absolute_position', (x, y)) # This is not good practice
        self.simulation_scene.addItem(car)
        return car
    
    def _update_scene(self):
        with self.environment.lock:
            self._change_lights()
            self._move_cars()

    def _move_cars(self):
        CAR_SIZE = 30
        # Add new cars and update existing ones
        for car_id in self.environment.cars:
            i, j = self.environment.cars[car_id]
            if car_id not in self.car_items:
                car_item = self._add_car(i, j, CAR_SIZE, CAR_SIZE, Qt.blue)
                self.car_items[car_id] = car_item
            else:
                car_item = self.car_items[car_id]
                x_previous, y_previous = car_item.absolute_position
                x, y = j * self.scale_factor, i * self.scale_factor

                car_item.setX(x - x_previous)
                car_item.setY(y - y_previous)

        # Remove unused cars
        cars_to_drop = []
        for car_id in self.car_items:
            if car_id not in self.environment.cars:
                cars_to_drop.append(car_id)
        
        for car_id in cars_to_drop:
            self.simulation_scene.removeItem(self.car_items[car_id])
            self.car_items.pop(car_id)
        

    def _change_lights(self):
        for semaphore_id in self.environment.semaphores:
            light_direction = self.environment.semaphores[semaphore_id]
            
            semaphore_item = self.semaphore_items[semaphore_id]
            for direction in semaphore_item.light_directions:
                if direction == light_direction:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.green))
                else:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.red))


app = QApplication(sys.argv)

with open("./matrices/matrix.pkl", 'rb') as file:
    matrix = pickle.load(file)
environment = Environment(matrix)
        
window = GraphicWindow(environment)
window.show()
app.exec_()