from enum import Enum
import os
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QScrollArea, QGridLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit
import pickle

from environment import Block, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_COLOR, Colors, Directions, valid_coordinates
from ui.tile import Tile

class _Widgets(Enum):
    add_road_button = 0
    remove_road_button = 1
    add_place_button = 2
    remove_place_button = 3
    save_button = 4
    stop_button = 5
    name_button = 6
    enter_name_button = 7
    enter_place_button = 8
    zoom_in_button = 9
    zoom_out_button = 10
    name_input = 11
    place_name_input = 12
    place_description_input = 13


class BuildWindow(QMainWindow):
    def __init__(self, height : int = 40, width : int = 40):
        super().__init__()
        self._map_name : str = ''
        self._grid_height = height
        self._grid_width = width
        self._tiles : list[list[Tile]] = []
        self._matrix : list[list[int]] = []
        self._add_road = False
        self._remove_road = False

        self.setWindowTitle("Build")
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self._control_widgets : dict[_Widgets, QWidget] = {}

        main_layout = QVBoxLayout()
        self._message_label = QLabel()
        main_layout.addWidget(self._message_label)
        
        core_layout = QHBoxLayout()

        # Control layout set up
        ## Buttons
        control_layout = QVBoxLayout()
        self._control_widgets[_Widgets.add_road_button] = QPushButton("Add Road")
        self._control_widgets[_Widgets.remove_road_button] = QPushButton("Remove Road")
        self._control_widgets[_Widgets.add_place_button] = QPushButton("Add Place")
        self._control_widgets[_Widgets.remove_place_button] = QPushButton("Remove Place")
        self._control_widgets[_Widgets.save_button] = QPushButton("Save")
        self._control_widgets[_Widgets.stop_button] = QPushButton("Stop")

        self._control_widgets[_Widgets.name_button] = QPushButton('Name')
        self._control_widgets[_Widgets.enter_name_button] = QPushButton('Enter')
        self._control_widgets[_Widgets.enter_place_button] = QPushButton('Enter')

        self._control_widgets[_Widgets.zoom_in_button] = QPushButton("+")
        self._control_widgets[_Widgets.zoom_out_button] = QPushButton("-")
        
        ## Text input
        self._control_widgets[_Widgets.name_input] = QLineEdit()
        self._control_widgets[_Widgets.place_name_input] = QLineEdit()
        self._control_widgets[_Widgets.place_description_input] = QLineEdit()

        ## Display required widgets
        self._show_widgets(self._home_widgets_predicate)

        ## Connect to handle events
        self._control_widgets[_Widgets.add_road_button].clicked.connect(self._handle_add_road)
        self._control_widgets[_Widgets.remove_road_button].clicked.connect(self._handle_remove_road)
        self._control_widgets[_Widgets.stop_button].clicked.connect(self._handle_stop)
        self._control_widgets[_Widgets.zoom_in_button].clicked.connect(self._handle_zoom_in)
        self._control_widgets[_Widgets.zoom_out_button].clicked.connect(self._handle_zoom_out)
        self._control_widgets[_Widgets.save_button].clicked.connect(self._handle_save)
        self._control_widgets[_Widgets.name_button].clicked.connect(self._handle_name)
        self._control_widgets[_Widgets.enter_name_button].clicked.connect(self._handle_enter_name)
        self._control_widgets[_Widgets.enter_place_button].clicked.connect(self._handle_enter_place)

        ## Wire with parent layout
        for widget in self._control_widgets.values():
            control_layout.addWidget(widget)

        # **Grid layout set up
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        grid_container = QWidget()
        grid_layout = QGridLayout(grid_container)
        
        self.grid = grid_layout

        # Add tiles to grid
        for i in range(height):
            self._tiles.append([])
            self._matrix.append([])
            for j in range(width):
                tile = Tile((i, j))
                tile.clicked.connect(self._handle_tile_clicked)
                grid_layout.addWidget(tile, i, j)
                self._tiles[i].append(tile)
                self._matrix[i].append(0)

        # **Wire up
        scroll_area.setWidget(grid_container)
        core_layout.addWidget(scroll_area)
        core_layout.addLayout(control_layout)
        main_layout.addLayout(core_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _handle_add_road(self):
        self._add_road = True
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.stop_button])

        self._paint_tiles(Colors.YELLOW, lambda i, j: self._matrix[i][j] == 0 and (i == 0 or j == 0 or i == self._grid_width - 1 or j == self._grid_height -1) and i != j and (i, j) != (0, self._grid_width - 1) and (i, j) != (self._grid_height - 1, 0))

    def _handle_remove_road(self):
        self._remove_road = True
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.stop_button])

    def _handle_name(self):
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.enter_name_button, _Widgets.name_input])
        self._control_widgets[_Widgets.name_input].setText(self._map_name)


    def _handle_save(self):
        if self._map_name == '':
            self._message_label.setText("You must name the map created")
            return
        
        self._message_label.setText("Saving")
        block_matrix : list[list[Block]] = []
        
        for i in range(self._grid_height):
            block_matrix.append([])
            
            for j in range(self._grid_width):
                direction = self._matrix[i][j]

                if direction == -1:
                    block_matrix[i].append(SemaphoreBlock((i, j), (i, j)))

                    offsets = [(-1, 0), (0, -1)]
                    for p, q in offsets:
                        neighbor_block = block_matrix[i + p][j + q]
                        if isinstance(neighbor_block, SemaphoreBlock):
                            block_matrix[i][j] = (SemaphoreBlock((i, j), neighbor_block.representative))
                            break

                elif direction != 0:
                    block_matrix[i].append(RoadBlock((i, j), direction))

                else:
                    block_matrix[i].append(None)

                    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                    for p, q in offsets:
                        if valid_coordinates(i + p, j + q, self._grid_height, self._grid_width) and self._matrix[i + p][j + q] != 0:
                            block_matrix[i][j] = SidewalkBlock((i, j), p == 0)
                            break
        
        if 'matrices' not in os.listdir('./src/ui/'):
            os.mkdir('./src/ui/matrices')

        # if f'{self._map_name}.pkl' in os.listdir('./src/ui/matrices'):
        #     self._message_label.setText('There is already a map named like that, please use other name')
        #     return
        
        with open(f"./src/ui/matrices/{self._map_name}.pkl", 'wb') as file:
            pickle.dump(block_matrix, file)
        self._message_label.setText("Map successfully saved")
        
    def _handle_stop(self):
        self._add_road = False
        self._remove_road = False

        self._show_widgets(self._home_widgets_predicate)

        self._paint_tiles(Colors.GREY, lambda i, j: self._matrix[i][j] == 0 and (i == 0 or j == 0 or i == self._grid_width - 1 or j == self._grid_height -1) and i != j and (i, j) != (0, self._grid_width - 1) and (i, j) != (self._grid_height - 1, 0))

    def _handle_zoom_in(self):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                self._tiles[i][j].resize(4)

    def _handle_zoom_out(self):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                self._tiles[i][j].resize(-4)
            
    def _handle_enter_name(self):
        self._map_name = self._control_widgets[_Widgets.name_input].text()
        self._show_widgets(self._home_widgets_predicate)
        print(self._map_name)

    def _handle_enter_place(self):
        pass

    def _handle_tile_clicked(self, coordinates : tuple[int, int]):
        i, j = coordinates
        direction = self._matrix[i][j]

        if self._add_road and direction == 0 and (i == 0 or j == 0 or i == self._grid_width - 1 or j == self._grid_height -1) and i != j and coordinates != (0, self._grid_width - 1) and coordinates != (self._grid_height - 1, 0):
            vertical = i == 0 or i == self._grid_height - 1
            if vertical:
                length = self._grid_height
                direction = Directions.SOUTH if i == 0 else Directions.NORTH
                color = DIRECTION_COLOR[direction]
            else:
                length = self._grid_width
                direction = Directions.EAST if j == 0 else Directions.WEST
                color = DIRECTION_COLOR[direction]

            for k in range(length):
                p = k if vertical else i
                q = j if vertical else k

                if self._matrix[p][q] != Directions.EMPTY:
                    self._matrix[p][q] = Directions.INTERSECTION
                    self._tiles[p][q].set_color(DIRECTION_COLOR[Directions.INTERSECTION])
                else:
                    self._tiles[p][q].set_color(color)
                    self._matrix[p][q] = direction
        elif self._remove_road and direction not in [Directions.EMPTY, Directions.INTERSECTION]:
            vertical = direction in [Directions.NORTH, Directions.SOUTH]
            length = self._grid_height if vertical else self._grid_width

            for k in range(length):
                p = k if vertical else i
                q = j if vertical else k
                
                if self._matrix[p][q] != Directions.INTERSECTION:
                    self._matrix[p][q] = Directions.EMPTY
                    self._tiles[p][q].set_color(DIRECTION_COLOR[Directions.EMPTY])
                else:
                    intersection_road : tuple[int, int] = None
                    for offset in [(0, 1), (0, -1)] if vertical else [(1, 0), (-1, 0)]:
                        vertical_offset, horizontal_offset = offset
                        p_prime = p + vertical_offset
                        q_prime = q + horizontal_offset

                        if self._matrix[p_prime][q_prime] not in [Directions.EMPTY, Directions.INTERSECTION]:
                            intersection_road = (p_prime, q_prime)
                            break
                    
                    if intersection_road == None:
                        self._matrix[p][q] = Directions.EMPTY
                        self._tiles[p][q].set_color(DIRECTION_COLOR[Directions.EMPTY])
                    else:
                        p_prime, q_prime = intersection_road
                        direction = self._matrix[p_prime][q_prime]
                        self._matrix[p][q] = direction
                        self._tiles[p][q].set_color(DIRECTION_COLOR[direction])

    def _show_widgets(self, predicate = lambda widget_id: True) -> None:
        for widget_id in self._control_widgets:
            if predicate(widget_id):
                self._control_widgets[widget_id].show()
            else:
                self._control_widgets[widget_id].hide()
    
    def _paint_tiles(self, color, predicate = lambda i, j: True):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                if predicate(i, j):
                    self._tiles[i][j].set_color(color)

    def _home_widgets_predicate(self, widget_id):
        return widget_id not in [_Widgets.stop_button, _Widgets.enter_name_button, _Widgets.enter_place_button, _Widgets.name_input, _Widgets.place_name_input, _Widgets.place_description_input]
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BuildWindow(20, 20)
    window.showMaximized()
    app.exec_()