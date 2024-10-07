import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QHBoxLayout, QScrollArea, QGridLayout, QVBoxLayout, QPushButton, QLabel, QRadioButton
import pickle
from functools import partial

from environment import Block, RoadBlock, SemaphoreBlock, SidewalkBlock
from globals import DIRECTION_COLOR, Colors, Directions, valid_coordinates
from ui.simulation_window import SimulationWindow
from ui.start_window import StartWindow
from ui.tile import Tile

class SelectionWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Selection")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)
        self.simulation_window : SimulationWindow = None
        self.home_window : StartWindow = None
        self.smart_semaphore = True

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        home_button = QPushButton("Back")
        home_button.setFixedSize(100, 30)
        home_button.clicked.connect(self._back_home)
        main_layout.addWidget(home_button)

        self.smart_button = QRadioButton("Smart Semaphore")
        self.smart_button.setFixedSize(300, 30)
        self.standard_button = QRadioButton("Standard Semaphore")
        self.standard_button.setFixedSize(300, 30)
        main_layout.addWidget(self.smart_button)
        main_layout.addWidget(self.standard_button)

        self.smart_button.setChecked(True)
        self.smart_button.toggled.connect(self._select_semaphore)
        self.standard_button.toggled.connect(self._select_semaphore)

        title_label = QLabel("Select a map:")
        title_label.setFont(QFont("Arial", 60, 500, True))
        main_layout.addWidget(title_label)

        maps = []
        for file_name in os.listdir('./src/ui/matrices'):
            if len(file_name) > 4 and file_name[len(file_name) - 4:] == '.pkl':
                maps.append(file_name[:len(file_name) - 4])
        
        for map in maps:
            button = QPushButton(map)
            button.clicked.emit()
            button.clicked.connect(partial(self._select_map, map))
            main_layout.addWidget(button)
            button.setFont(QFont("Arial", 30, 50, False))
        
        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _select_map(self, map_name : str):
        self.simulation_window = SimulationWindow(f'./src/ui/matrices/{map_name}.pkl', self.smart_semaphore)
        self.simulation_window.showMaximized()
        self.close()

    def _select_semaphore(self):
        if self.smart_button.isChecked():
            self.smart_semaphore = True
        elif self.standard_button.isChecked():
            self.smart_semaphore = False

    def _back_home(self):
        self.home_window = StartWindow()
        self.home_window.showMaximized()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionWindow()
    window.showMaximized()
    app.exec_()