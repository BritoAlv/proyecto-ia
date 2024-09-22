from math import ceil
import pickle
import sys
from uuid import UUID
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtCore import Qt, QTimer, QPointF
from PyQt5.QtGui import QBrush, QPolygonF

from environment import Environment, RoadBlock, SemaphoreBlock, SidewalkBlock

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.zoom_factor = 1.15

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:  # Scroll up (zoom in)
            self.scale(self.zoom_factor, self.zoom_factor)
        else:  # Scroll down (zoom out)
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)


class GraphicWindow(QWidget):
    def __init__(self, environment : Environment):
        super().__init__()

        self.scale_factor = 60
        self.environment = environment
        self.car_items : dict[UUID, QGraphicsItem] = {}

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
        self.timer.timeout.connect(self._move_cars)
        self.timer.start(1000)

    def _build_simulation_scene(self):
        SIDEWALK_WIDTH = 40
        ROAD_WIDTH = 70

        matrix = self.environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        # Set background
        background = QGraphicsRectItem(0, 0, width * self.scale_factor, height * self.scale_factor)
        background.setBrush(QBrush(Qt.darkGreen))
        self.simulation_scene.addItem(background)

        # Set horizontal roads
        for i in range(height):
            for j in [0, width - 1]:
                if isinstance(matrix[i][j], RoadBlock):
                    self._add_road(j * self.scale_factor, i * self.scale_factor, width * self.scale_factor, ROAD_WIDTH, Qt.lightGray)
                    break
        
        # Set vertical roads
        for j in range(width):
            for i in [0, height - 1]:   
                if isinstance(matrix[i][j], RoadBlock):
                    self._add_road(j * self.scale_factor, i * self.scale_factor, ROAD_WIDTH, height * self.scale_factor, Qt.lightGray)
                    break

    def _add_road(self, x : int, y : int, width : int, height : int, color : Qt.BrushStyle):
        road = QGraphicsRectItem(x, y, width, height)
        road.setBrush(QBrush(color))
        self.simulation_scene.addItem(road)
    
    def _add_car(self, x : int, y : int, width : int, height : int, color : Qt.BrushStyle):
        # Define the triangle's vertices
        points = QPolygonF([
            QPointF(x, y),                   # Top vertex
            QPointF(x - width / 2, y + height),  # Bottom left vertex
            QPointF(x + width / 2, y + height)   # Bottom right vertex
        ])
        
        # Create the polygon item and set its brush color
        car = QGraphicsPolygonItem(points)
        car.setBrush(QBrush(color))
        self.simulation_scene.addItem(car)
        return car

    def _move_cars(self):
        CAR_SIZE = 30
        # Add new cars and update existing ones
        with self.environment.lock:
            for car_id in self.environment.cars:
                i, j = self.environment.cars[car_id]
                if car_id not in self.car_items:
                    car_item = self._add_car(j * self.scale_factor, i * self.scale_factor, CAR_SIZE, CAR_SIZE, Qt.blue)
                    self.car_items[car_id] = car_item
                else:
                    car_item = self.car_items[car_id]
                    car_item.setPos(QPointF(j * self.scale_factor, i * self.scale_factor))

            # Remove unused cars
            cars_to_drop = []
            for car_id in self.car_items:
                if car_id not in self.environment.cars:
                    cars_to_drop.append(car_id)
            
            for car_id in cars_to_drop:
                self.simulation_scene.removeItem(self.car_items[car_id])
                self.car_items.pop(car_id)

app = QApplication(sys.argv)

with open("matrix.pkl", 'rb') as file:
    matrix = pickle.load(file)
environment = Environment(matrix)
        
window = GraphicWindow(environment)
window.show()
app.exec_()