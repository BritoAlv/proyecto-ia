from enum import Enum
import os
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QScrollArea, QGridLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QTextEdit
import pickle

from environment import Block, PlaceBlock, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_COLOR, DIRECTION_OFFSETS, Colors, Directions, valid_coordinates
from ui.start_window import StartWindow
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
    back_home_button = 14


class BuildWindow(QMainWindow):
    def __init__(self, height : int = 40, width : int = 40):
        super().__init__()
        self._map_name : str = ''
        self._grid_height = height
        self._grid_width = width
        self._tiles : list[list[Tile]] = []
        self._matrix : list[list[int]] = []
        self._places : dict[tuple[int, int], tuple[str, str]] = {}
        self._add_road = False
        self._remove_road = False
        self._add_place = False
        self._current_place : tuple[int, int] = None

        self.setWindowTitle("Build")
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        self._control_widgets : dict[_Widgets, QWidget] = {}
        self._home_window = None

        main_layout = QVBoxLayout()
        self._message_label = QLabel()
        main_layout.addWidget(self._message_label)
        
        core_layout = QHBoxLayout()

        # Control layout set up
        control_layout = QVBoxLayout()
        self._control_widgets[_Widgets.back_home_button] = QPushButton('Back Home')
        self._control_widgets[_Widgets.add_road_button] = QPushButton("Add Road")
        self._control_widgets[_Widgets.remove_road_button] = QPushButton("Remove Road")
        self._control_widgets[_Widgets.add_place_button] = QPushButton("Add Place")
        self._control_widgets[_Widgets.remove_place_button] = QPushButton("Remove Place")
        self._control_widgets[_Widgets.save_button] = QPushButton("Save")
        self._control_widgets[_Widgets.name_button] = QPushButton('Name')

        self._control_widgets[_Widgets.name_input] = QLineEdit()
        self._control_widgets[_Widgets.name_input].setPlaceholderText("Map's name")
        self._control_widgets[_Widgets.enter_name_button] = QPushButton('Enter')

        self._control_widgets[_Widgets.place_name_input] = QLineEdit()
        self._control_widgets[_Widgets.place_name_input].setPlaceholderText("Place's name")
        self._control_widgets[_Widgets.place_description_input] = QTextEdit()
        self._control_widgets[_Widgets.place_description_input].setPlaceholderText("Place's description")
        self._control_widgets[_Widgets.enter_place_button] = QPushButton('Enter')

        self._control_widgets[_Widgets.stop_button] = QPushButton("Stop")
        self._control_widgets[_Widgets.zoom_in_button] = QPushButton("+")
        self._control_widgets[_Widgets.zoom_out_button] = QPushButton("-")

        ## Display required widgets
        self._show_widgets(self._home_widgets_predicate)

        ## Connect to handle events
        self._control_widgets[_Widgets.back_home_button].clicked.connect(self._handle_back_home)
        self._control_widgets[_Widgets.add_road_button].clicked.connect(self._handle_add_road)
        self._control_widgets[_Widgets.remove_road_button].clicked.connect(self._handle_remove_road)
        self._control_widgets[_Widgets.stop_button].clicked.connect(self._handle_stop)
        self._control_widgets[_Widgets.zoom_in_button].clicked.connect(self._handle_zoom_in)
        self._control_widgets[_Widgets.zoom_out_button].clicked.connect(self._handle_zoom_out)
        self._control_widgets[_Widgets.save_button].clicked.connect(self._handle_save)
        self._control_widgets[_Widgets.name_button].clicked.connect(self._handle_name)
        self._control_widgets[_Widgets.enter_name_button].clicked.connect(self._handle_enter_name)
        self._control_widgets[_Widgets.add_place_button].clicked.connect(self._handle_add_place)
        self._control_widgets[_Widgets.remove_place_button].clicked.connect(self._handle_remove_place)
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
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.stop_button, _Widgets.zoom_in_button, _Widgets.zoom_out_button])

        self._paint_tiles(Colors.YELLOW, self._map_border_predicate)

    def _handle_remove_road(self):
        self._remove_road = True
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.stop_button, _Widgets.zoom_in_button, _Widgets.zoom_out_button])

    def _handle_name(self):
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.enter_name_button, _Widgets.name_input])
        self._control_widgets[_Widgets.name_input].setText(self._map_name)


    def _handle_save(self):
        print(self._map_name)
        if self._map_name == '':
            self._message_label.setText("You must name the map created")
            return
        
        self._message_label.setText("Saving")
        block_matrix : list[list[Block]] = []
        
        for i in range(self._grid_height):
            block_matrix.append([])
            
            for j in range(self._grid_width):
                if i == 0 or j == 0 or i == self._grid_height - 1 or j == self._grid_width - 1:
                    block_matrix[i].append(SidewalkBlock((i, j), i == 0 or i == self._grid_height - 1))
                    continue

                direction = self._matrix[i][j]

                if direction == Directions.INTERSECTION:
                    block_matrix[i].append(SemaphoreBlock((i, j), (i, j)))

                    offsets = [(-1, 0), (0, -1)]
                    for p, q in offsets:
                        neighbor_block = block_matrix[i + p][j + q]
                        if isinstance(neighbor_block, SemaphoreBlock):
                            block_matrix[i][j] = (SemaphoreBlock((i, j), neighbor_block.representative))
                            break
                
                elif direction == Directions.PLACE:
                    two_offsets = [(2, 0), (-2, 0), (0, 2), (0, -2)]
                    name, description = self._places[i, j]

                    representative : tuple[int, int] = None
                    for p, q in two_offsets:
                        x, y = i + p, j + q

                        if not valid_coordinates(x, y, self._grid_height, self._grid_width):
                            continue

                        if self._matrix[x][y] in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                            representative = x, y

                    block_matrix[i].append(PlaceBlock((i, j), name, description, representative))

                elif direction != Directions.EMPTY:
                    block_matrix[i].append(RoadBlock((i, j), direction))

                else:
                    block_matrix[i].append(None)

                    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                    for p, q in offsets:
                        if valid_coordinates(i + p, j + q, self._grid_height, self._grid_width) and self._matrix[i + p][j + q] not in [Directions.EMPTY, Directions.PLACE]:
                            block_matrix[i][j] = SidewalkBlock((i, j), p == 0)
                            break
        
        if 'matrices' not in os.listdir('./src/ui/'):
            os.mkdir('./src/ui/matrices')

        # # Avoid create a map with an existing name
        # if f'{self._map_name}.pkl' in os.listdir('./src/ui/matrices'):
        #     self._message_label.setText('There is already a map named like that, please use other name')
        #     return

        # Verify map's empty
        map_empty = True
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                if isinstance(block_matrix[i][j], RoadBlock):
                    map_empty = False
                    break
        if map_empty:
            self._message_label.setText('Cannot save an empty map')
            return
        
        with open(f"./src/ui/matrices/{self._map_name}.pkl", 'wb') as file:
            pickle.dump(block_matrix, file)
        self._message_label.setText("Map successfully saved")
        
    def _handle_stop(self):
        self._add_road = False
        self._remove_road = False
        self._add_place = False
        self._current_place = None

        self._show_widgets(self._home_widgets_predicate)

        self._paint_tiles(Colors.GREY, self._map_border_predicate)
        self._paint_tiles(Colors.GREY, self._available_place_predicate)

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
        self._handle_stop()

    def _handle_add_place(self):
        self._add_place = True
        self._show_widgets(lambda widget_id: widget_id in [_Widgets.place_name_input, _Widgets.place_description_input, _Widgets.zoom_in_button, _Widgets.zoom_out_button, _Widgets.enter_place_button])

        self._paint_tiles(Colors.CYAN, self._available_place_predicate)
    

    def _handle_remove_place(self):
        pass

    def _handle_enter_place(self):
        place_name = self._control_widgets[_Widgets.place_name_input].text()
        place_description = self._control_widgets[_Widgets.place_description_input].toPlainText()

        if place_name == '':
            self._message_label.setText('Must give a name to the interest place')
            return 

        self._places[self._current_place] = place_name, place_description
        self._control_widgets[_Widgets.place_name_input].setText('')
        self._control_widgets[_Widgets.place_description_input].setText('')
        self._handle_stop()


    def _handle_back_home(self):
        self._home_window = StartWindow()
        self._home_window.showMaximized()
        self.close()

    def _handle_tile_clicked(self, coordinates : tuple[int, int]):
        i, j = coordinates
        direction = self._matrix[i][j]

        if self._add_road and self._map_border_predicate(i, j):
            vertical = i == 0 or i == self._grid_height - 1
            if vertical:
                length = self._grid_height - 2
                direction = Directions.SOUTH if i == 0 else Directions.NORTH
                color = DIRECTION_COLOR[direction]

                # Avoid start-row to be able to generate a new road
                self._matrix[0][j] = self._matrix[self._grid_height - 1][j] = Directions.EOR
                self._tiles[0][j].set_color(Colors.BLACK)
                self._tiles[self._grid_height - 1][j].set_color(Colors.BLACK)
            else:
                length = self._grid_width - 2
                direction = Directions.EAST if j == 0 else Directions.WEST
                color = DIRECTION_COLOR[direction]

                # Avoid start-column to be able to generate a new road
                self._matrix[i][0] = self._matrix[i][self._grid_width - 1] = Directions.EOR
                self._tiles[i][0].set_color(Colors.BLACK)
                self._tiles[i][self._grid_width - 1].set_color(Colors.BLACK)

            for k in range(length):
                k += 1

                p = k if vertical else i
                q = j if vertical else k

                if self._matrix[p][q] != Directions.EMPTY:
                    self._matrix[p][q] = Directions.INTERSECTION
                    self._tiles[p][q].set_color(DIRECTION_COLOR[Directions.INTERSECTION])
                else:
                    self._tiles[p][q].set_color(color)
                    self._matrix[p][q] = direction
        elif self._remove_road and direction not in [Directions.EMPTY, Directions.INTERSECTION, Directions.PLACE]:
            vertical = direction in [Directions.NORTH, Directions.SOUTH]
            length = self._grid_height - 2 if vertical else self._grid_width - 2

            if vertical:
                # Enable start-row
                self._matrix[0][j] = self._matrix[self._grid_height - 1][j] = Directions.EMPTY
                self._tiles[0][j].set_color(DIRECTION_COLOR[Directions.EMPTY])
                self._tiles[self._grid_height - 1][j].set_color(DIRECTION_COLOR[Directions.EMPTY])
            else:
                # Enable start-column
                self._matrix[i][0] = self._matrix[i][self._grid_width - 1] = Directions.EMPTY
                self._tiles[i][0].set_color(DIRECTION_COLOR[Directions.EMPTY])
                self._tiles[i][self._grid_width - 1].set_color(DIRECTION_COLOR[Directions.EMPTY])

            for k in range(length):
                k += 1
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

        elif self._add_place and self._available_place_predicate(i, j):
            self._matrix[i][j] = Directions.PLACE
            self._tiles[i][j].set_color(DIRECTION_COLOR[Directions.PLACE])
            self._add_place = False
            self._current_place = i, j

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
    
    def _map_border_predicate(self, i : int, j : int):
        first_border = (i == 0 or j == 0 or i == self._grid_height - 1 or j == self._grid_width - 1)

        no_corner =  (i, j) != (0, 0) and (i, j) != (self._grid_height - 1, self._grid_width - 1) and (i, j) != (0, self._grid_width - 1) and (i, j) != (self._grid_height - 1, 0)

        # second_border = (i == 1 or j == 1 or i == self._grid_height - 2 or j == self._grid_width - 2)
        # no_corner =  (i, j) != (1, 1) and (i, j) != (self._grid_height - 2, self._grid_width - 2) and (i, j) != (1, self._grid_width - 2) and (i, j) != (self._grid_height - 2, 1)
        # no_first_border = i != 0 and j != 0 and i != self._grid_height - 1 and j != self._grid_width - 1

        return self._matrix[i][j] == 0 and first_border and no_corner
    
    def _available_place_predicate(self, i : int, j : int):
        two_offsets = [(2, 0), (-2, 0), (0, 2), (0, -2)]

        for p, q in DIRECTION_OFFSETS.values():
            x = i + p
            y = j + q

            if not valid_coordinates(x, y, self._grid_height, self._grid_width):
                continue
                
            if self._matrix[i][j] == Directions.EMPTY and self._matrix[x][y] in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                return False

        for p, q in two_offsets:
            x = i + p
            y = j + q

            if not valid_coordinates(x, y, self._grid_height, self._grid_width):
                continue
                
            if self._matrix[i][j] == Directions.EMPTY and self._matrix[x][y] in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                return True
        
        return False
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BuildWindow(20, 20)
    window.showMaximized()
    app.exec_()

a = QTextEdit()