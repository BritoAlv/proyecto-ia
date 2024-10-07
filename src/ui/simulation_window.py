from datetime import datetime, timedelta
from functools import partial
import os
import pickle
from queue import PriorityQueue
import sys
from uuid import UUID
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsItem,
    QGraphicsTextItem,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QFont

from environment import (
    Environment,
    PlaceBlock,
    RoadBlock,
    SemaphoreBlock,
    SidewalkBlock,
)
from globals import DIRECTION_OFFSETS, Directions, valid_coordinates
from sim.MovingAgent import MovingAgent
from sim.Event import Event, EventHandler, EventType
from ui.stats_window import StatsWindow


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
        self.light_directions: dict[int, QGraphicsItem] = {}


class SimulationWindow(QWidget):
    def __init__(self, matrix_path: str, use_fuzzy: bool = True):
        super().__init__()

        # Load matrix data into main memory
        with open(matrix_path, "rb") as file:
            matrix = pickle.load(file)
        environment = Environment(os.path.basename(matrix_path)[:-4], matrix, use_fuzzy=use_fuzzy)

        # Business (simulation) logic properties
        self._environment = environment  ## Core data structure
        self._event_handler = EventHandler(environment) 

        ## Simulation properties
        self._events_queue: PriorityQueue[Event] = PriorityQueue()
        self._event: Event = Event(self._environment.date + timedelta(seconds=1), EventType.CAR_EVENT)
        self._timer_period: int = 300
        self._simulation_on = False
        self._seed_events()

        ## Properties to display agents
        self._car_items: dict[UUID, QGraphicsItem] = {}
        self._walker_items: dict[UUID, QGraphicsItem] = {}
        self._semaphore_items: dict[tuple[int, int], SemaphoreItem] = {}

        self._stats_window: StatsWindow = None  # Reference to window
        self._scale_factor = 60  ## Scale factor to visualize items

        ## Properties to display labels
        self._cars = {}
        self._agent_labels = {}

        # Create and connect timer to handle the simulation loop
        self._timer = QTimer()

        self._timer.timeout.connect(self._simulate) # Use this line for debug
        # self._timer.timeout.connect(partial(self._simulate, False)) # Use this line for production

        # Visualization setup
        self.setWindowTitle("Simulation")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )

        ## Add a horizontal top-layout to hold control buttons
        top_layout = QHBoxLayout()

        ### Setup control buttons
        start_button = QPushButton("Start")
        start_button.setFixedSize(200, 30)
        stop_button = QPushButton("Stop")
        stop_button.setFixedSize(200, 30)
        end_button = QPushButton("End and see results")
        end_button.setFixedSize(200, 30)
        faster_button = QPushButton("Faster")
        faster_button.setFixedSize(200, 30)
        slower_button = QPushButton("Slower")
        slower_button.setFixedSize(200, 30)
        self._date_label = QLabel(text=self._environment.date.__str__())

        start_button.clicked.connect(self._handle_start)
        stop_button.clicked.connect(self._handle_stop)
        end_button.clicked.connect(self._handle_end)
        faster_button.clicked.connect(self._handle_faster)
        slower_button.clicked.connect(self._handle_slower)

        top_layout.addWidget(start_button)
        top_layout.addWidget(stop_button)
        top_layout.addWidget(end_button)
        top_layout.addWidget(faster_button)
        top_layout.addWidget(slower_button)
        top_layout.addWidget(self._date_label)

        main_layout.addLayout(top_layout)

        ## Add view and simulation scene to visualize the actual map with all events
        self.view = ZoomableGraphicsView()
        self.simulation_scene = QGraphicsScene()
        self._build_simulation_scene()
        self.view.setScene(self.simulation_scene)

        main_layout.addWidget(self.view)
        self.setLayout(main_layout)

    def _seed_events(self):
        ### Seed a rain-event
        self._events_queue.put(Event(self._environment.date + timedelta(seconds=2), EventType.RAIN_EVENT))
        # Seed a walker-event
        self._events_queue.put(Event(self._environment.date + timedelta(seconds=2), EventType.WALKER_EVENT))

    def _simulate(self, debug: bool = True):
        """
        Core simulation method, it holds an iteration over the simulation loop
        """

        if not debug:
            # Handle events
            while self._event.date == self._environment.date:
                future_event = self._event_handler.handle(self._event)
                self._events_queue.put(future_event)
                self._event = self._events_queue.get()

        # Convert dictionary values to list (in three cases) to avoid dictionary overwriting while iterating
        for semaphore in list(self._environment.semaphores.values()):
            semaphore.act()

        for car in list(self._environment.cars.values()):
            car.act()

        for walker in list(self._environment.walkers.values()):
            walker.act()

        self._update_scene()

        # Increase simulation date
        self._environment.increase_date()
        
        if self._environment.date > datetime(2000, 1, 8, 0, 0):
            self._handle_end()

    def _handle_start(self):
        self._simulation_on = True
        self._timer.start(self._timer_period)

    def _handle_stop(self):
        self._simulation_on = False
        self._timer.stop()

    def _handle_end(self):
        self._timer.stop()
        self._stats_window = StatsWindow(self._environment)
        self._stats_window.showMaximized()

        self.close()

    def _handle_faster(self):
        if not self._simulation_on or self._timer_period <= 1:
            return

        if self._timer_period <= 10:
            self._timer_period -= 1
        elif self._timer_period <= 50:
            self._timer_period -= 10
        else:
            self._timer_period -= 50

        self._handle_stop()
        self._handle_start()
    
    def _handle_slower(self):
        if not self._simulation_on or self._timer_period >= 1000:
            return
        
        if self._timer_period < 50:
            self._timer_period = 50
        else:
            self._timer_period += 50

        self._handle_stop()
        self._handle_start()
        

    def _build_simulation_scene(self):
        matrix = self._environment.matrix
        height = len(matrix)
        width = len(matrix[0])

        # Set background
        background = QGraphicsRectItem(
            0, 0, width * self._scale_factor, height * self._scale_factor
        )
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

                rectangle = self._add_rectangle(
                    i, j, self._scale_factor, self._scale_factor, color
                )

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
                        sub_rect = self._create_sem_rectangle(
                            rectangle.rect().x(),
                            rectangle.rect().y(),
                            rectangle.rect().width(), 
                            rectangle.rect().height(),
                            block.direction,
                        )
                        sub_rect.setBrush(QBrush(Qt.red))
                        sub_rect.setZValue(1)
                        self.simulation_scene.addItem(sub_rect)
                        self._semaphore_items[representative].light_directions[
                            block.direction
                        ] = sub_rect

                if isinstance(block, RoadBlock):
                    pos = f" ({i}, {j})"
                    if block.direction == Directions.NORTH:
                        self._add_text("N" + pos, i, j)
                    elif block.direction == Directions.SOUTH:
                        self._add_text("S" + pos, i, j)
                    elif block.direction == Directions.EAST:
                        self._add_text("E" + pos, i, j)
                    elif block.direction == Directions.WEST:
                        self._add_text("W" + pos, i, j)

    def _add_rectangle(
        self, i: int, j: int, width: int, height: int, color: Qt.BrushStyle
    ) -> QGraphicsRectItem:
        x = j * self._scale_factor
        y = i * self._scale_factor

        rectangle = QGraphicsRectItem(x, y, width, height)
        rectangle.setBrush(QBrush(color))
        rectangle.__setattr__("absolute_position", (x, y))  # This is not good practice
        self.simulation_scene.addItem(rectangle)
        return rectangle

    def __add_text__(self, text: str, x: float, y: float):
        text_item = QGraphicsTextItem(text)
        font = QFont("Arial", 8, QFont.Thin)
        text_item.setFont(font)
        text_item.setPos(x, y)
        self.simulation_scene.addItem(text_item)
        return text_item

    def _add_text(self, text: str, i: int, j: int):
        return self.__add_text__(text, j * self._scale_factor, i * self._scale_factor)

    def _update_scene(self):
        self._date_label.setText(self._environment.date.__str__()) 
        self._change_lights()
        self._move_agent(self._environment.cars, self._car_items)
        self._move_agent(self._environment.walkers, self._walker_items, Qt.cyan, 15)

    def _change_lights(self):
        for semaphore_id in self._environment.semaphores:
            light_direction = self._environment.semaphores[semaphore_id].current

            semaphore_item = self._semaphore_items[semaphore_id]
            for direction in semaphore_item.light_directions:
                if direction == light_direction:
                    semaphore_item.light_directions[direction].setBrush(
                        QBrush(Qt.green)
                    )
                else:
                    semaphore_item.light_directions[direction].setBrush(QBrush(Qt.red))

    def _move_agent(
        self,
        environment_agents: dict[UUID, MovingAgent],
        scene_items: dict[UUID, QGraphicsItem],
        color: Qt.BrushStyle = Qt.blue,
        agent_size: int = 30,
    ):
        # Add new agent and update existing ones
        for agent_id in environment_agents:
            i, j = environment_agents[agent_id].position
            if agent_id not in scene_items:
                agent_item = self._add_rectangle(i, j, agent_size, agent_size, color)
                self._agent_labels[agent_id] = self.__add_text__(
                    str(environment_agents[agent_id].gui_label),
                    agent_item.x(),
                    agent_item.y(),
                )
                scene_items[agent_id] = agent_item
            else:
                agent_item = scene_items[agent_id]
                x_previous, y_previous = agent_item.absolute_position
                x, y = j * self._scale_factor, i * self._scale_factor

                scaled_offset = self._scale_factor / 3.5
                agent_item.setX(x - x_previous + scaled_offset)
                agent_item.setY(y - y_previous + scaled_offset)
                self._agent_labels[agent_id].setPos(
                    x + scaled_offset, y + scaled_offset
                )
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

    def _create_sem_rectangle(
        self, x: float, y: float, dx: float, dy: float, direction: Directions
    ) -> QGraphicsRectItem:
        if direction == Directions.NORTH:
            coordinates = self.get_north_sub_rectangle(x, y, dx, dy)
        if direction == Directions.SOUTH:
            coordinates = self.get_south_sub_rectangle(x, y, dx, dy)
        if direction == Directions.EAST:
            coordinates = self.get_west_sub_rectangle(x, y, dx, dy)
        if direction == Directions.WEST:
            coordinates = self.get_east_sub_rectangle(x, y, dx, dy)

        sub_rect = QGraphicsRectItem(coordinates[0], coordinates[1], coordinates[2], coordinates[3])
        return sub_rect

    def get_north_sub_rectangle(self, x, y, dx, dy):
        x_N = x + dx / 20
        dx_N = dx * 18 / 20
        y_N = y + dy / 20
        dy_N = dy / 20
        return (x_N, y_N, dx_N, dy_N)

    def get_south_sub_rectangle(self, x, y, dx, dy):
        x_N = x + dx / 20
        dx_N = dx * 18 / 20
        y_N = y + dy * 18 / 20
        dy_N = dy / 20
        return (x_N, y_N, dx_N, dy_N)

    def get_west_sub_rectangle(self, x, y, dx, dy):
        x_N = x + dx * 18 / 20
        dx_N = dx * 1 / 20
        y_N = y + dy / 20
        dy_N = dy * 18 / 20
        return (x_N, y_N, dx_N, dy_N)

    def get_east_sub_rectangle(self, x, y, dx, dy):
        x_N = x + dx / 20
        dx_N = dx * 1 / 20
        y_N = y + dy / 20
        dy_N = dy * 18 / 20
        return (x_N, y_N, dx_N, dy_N)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimulationWindow("./src/ui/matrices/f.pkl")
    window.showMaximized()
    app.exec_()
