import sys
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QScrollArea, QGridLayout, QVBoxLayout, QPushButton
import pickle

from environment import Block, RoadBlock, SemaphoreBlock, SidewalkBlock
from ui.globals import DIRECTION_COLOR, Colors, Directions, valid_coordinates
from ui.tile import Tile

class GridWindow(QMainWindow):
    def __init__(self, height : int = 40, width : int = 40):
        super().__init__()
        self._grid_height = height
        self._grid_width = width
        self._tiles : list[list[Tile]] = []
        self._matrix : list[list[int]] = []
        self._add_road = False
        self._remove_road = False

        self.setWindowTitle("Grid Window")
        self.setMinimumWidth(300)
        self.setMinimumHeight(300)

        main_layout = QHBoxLayout()

        # **Control layout set up
        buttons_layout = QVBoxLayout()
        self.add_road_button = QPushButton("Add Road")
        self.remove_road_button = QPushButton("Remove Road")
        self.add_place_button = QPushButton("Add Place")
        self.remove_place_button = QPushButton("Remove Place")
        self.save_button = QPushButton("Save")
        self.stop_button = QPushButton("Stop")
        self.zoom_in_button = QPushButton("+")
        self.zoom_out_button = QPushButton("-")
        self.stop_button.hide()

        self.add_road_button.clicked.connect(self._handle_add_road)
        self.remove_road_button.clicked.connect(self._handle_remove_road)
        self.stop_button.clicked.connect(self._handle_stop)
        self.zoom_in_button.clicked.connect(self._handle_zoom_in)
        self.zoom_out_button.clicked.connect(self._handle_zoom_out)
        self.save_button.clicked.connect(self._handle_save)

        buttons_layout.addWidget(self.add_road_button)
        buttons_layout.addWidget(self.remove_road_button)
        buttons_layout.addWidget(self.add_place_button)
        buttons_layout.addWidget(self.remove_place_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.zoom_in_button)
        buttons_layout.addWidget(self.zoom_out_button)
        buttons_layout.addWidget(self.stop_button)

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
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(buttons_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _handle_add_road(self):
        self._add_road = True
        self._hide_buttons()
        self._paint_tiles(Colors.YELLOW, lambda i, j: self._matrix[i][j] == 0 and (i == 0 or j == 0 or i == self._grid_width - 1 or j == self._grid_height -1) and i != j and (i, j) != (0, self._grid_width - 1) and (i, j) != (self._grid_height - 1, 0))

    def _handle_remove_road(self):
        self._remove_road = True
        self._hide_buttons()

    def _handle_save(self):
        block_matrix : list[list[Block]] = []
        
        for i in range(self._grid_height):
            block_matrix.append([])
            for j in range(self._grid_width):
                direction = self._matrix[i][j]
                if direction == -1:
                    block_matrix[i].append(SemaphoreBlock((i, j)))
                elif direction != 0:
                    block_matrix[i].append(RoadBlock((i, j), direction))
                else:
                    block_matrix[i].append(None)

                    offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]
                    for p, q in offsets:
                        if valid_coordinates(i + p, j + q, self._grid_height, self._grid_width) and self._matrix[i + p][j + q] != 0:
                            block_matrix[i][j] = SidewalkBlock((i, j), p == 0)
                            break

        with open("./matrices/matrix.pkl", 'wb') as file:
            file.write(pickle.dumps(block_matrix))
        
    def _handle_stop(self):
        self._add_road = False
        self._remove_road = False
        self._show_buttons()
        self._paint_tiles(Colors.GREY, lambda i, j: self._matrix[i][j] == 0 and (i == 0 or j == 0 or i == self._grid_width - 1 or j == self._grid_height -1) and i != j and (i, j) != (0, self._grid_width - 1) and (i, j) != (self._grid_height - 1, 0))

    def _handle_zoom_in(self):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                self._tiles[i][j].resize(4)

    def _handle_zoom_out(self):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                self._tiles[i][j].resize(-4)
    
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
        elif self.remove_road_button and direction not in [Directions.EMPTY, Directions.INTERSECTION]:
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
            

    def _show_buttons(self):
        self.add_road_button.show()
        self.remove_road_button.show()
        self.add_place_button.show()
        self.remove_place_button.show()
        self.save_button.show()
        self.stop_button.hide()
    
    def _hide_buttons(self):
        self.add_road_button.hide()
        self.remove_road_button.hide()
        self.add_place_button.hide()
        self.remove_place_button.hide()
        self.save_button.hide()
        self.stop_button.show()

    def _paint_tiles(self, color, predicate = lambda i, j: True):
        for i in range(self._grid_height):
            for j in range(self._grid_width):
                if predicate(i, j):
                    self._tiles[i][j].set_color(color)
        
app = QApplication(sys.argv)
window = GridWindow(20, 20)
window.show()
app.exec_()