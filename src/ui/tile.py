from math import ceil, floor
from PyQt5.QtCore import QEvent, Qt, pyqtSignal, QSize
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QMouseEvent, QPalette, QEnterEvent

from ui.globals import Colors

class Tile(QWidget):
    hovered = pyqtSignal(bool)
    clicked = pyqtSignal(tuple)

    def __init__(self, coordinates : tuple[int, int], color : str = Colors.GREY) -> None:
        super().__init__()
        self.setAutoFillBackground(True)
        self.minimum_dimension = 12
        
        self.setFixedHeight(self.minimum_dimension * 3)
        self.setFixedWidth(self.minimum_dimension * 3)
        
        self.coordinates = coordinates
        self.set_color(color)
    
    def enterEvent(self, event: QEnterEvent | None) -> None:
        self.hovered.emit(True)

    def leaveEvent(self, event: QEvent | None) -> None:
        self.hovered.emit(False)

    def mousePressEvent(self, a0: QMouseEvent | None) -> None:
        self.clicked.emit(self.coordinates)

    def set_color(self, color : str):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

    def resize(self, offset : int = 1):
        FACTOR = 5
        height = self.height()
        width = self.width()

        if self.minimum_dimension <= height <= self.minimum_dimension * FACTOR or (height > self.minimum_dimension * FACTOR and offset < 0) or (height < self.minimum_dimension and offset > 0):
            self.setFixedHeight(width + offset)
            self.setFixedWidth(width + offset)