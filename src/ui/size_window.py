import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel, QSpinBox

from ui.build_window import BuildWindow
from ui.start_window import StartWindow

class SizeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Traffic Sim")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)
        self.home_window = None
        self.build_window = None

        main_layout = QVBoxLayout()
        # main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        home_button = QPushButton("Back")
        home_button.setFixedSize(100, 30)

        title_label = QLabel("Map dimensions")
        title_label.setFont(QFont("Arial", 60, 500, True))

        width_label = QLabel('Width')
        self.width_spin_box = QSpinBox()
        self.width_spin_box.setRange(10, 100)
        self.width_spin_box.setValue(20)

        height_label = QLabel('Height')
        self.height_spin_box = QSpinBox()
        self.height_spin_box.setRange(10, 100)
        self.height_spin_box.setValue(20)

        width_label.setFont(QFont("Arial", 30, 500, False))
        height_label.setFont(QFont("Arial", 30, 500, False))

        enter_button = QPushButton("Create a map")

        home_button.clicked.connect(self._back_home)
        enter_button.clicked.connect(self._handle_enter)
        
        main_layout.addWidget(home_button)
        main_layout.addWidget(title_label)
        main_layout.addWidget(width_label)
        main_layout.addWidget(self.width_spin_box)
        main_layout.addWidget(height_label)
        main_layout.addWidget(self.height_spin_box)
        main_layout.addWidget(enter_button)


        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _handle_enter(self):
        self.build_window = BuildWindow(self.height_spin_box.value(), self.width_spin_box.value())
        self.build_window.showMaximized()
        self.close()

    def _back_home(self):
        self.home_window = StartWindow()
        self.home_window.showMaximized()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SizeWindow()
    window.showMaximized()
    app.exec_()