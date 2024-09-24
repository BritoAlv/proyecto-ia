import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow, QVBoxLayout, QPushButton, QLabel

class StartWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Traffic Sim")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)
        self.selection_window = None

        main_layout = QVBoxLayout()
        # main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel("Traffic Sim")
        title_label.setFont(QFont("Arial", 60, 500, True))

        build_button = QPushButton("Create a map")
        select_button = QPushButton("Select a map")
        build_button.setFont(QFont("Arial", 30, 50, False))
        select_button.setFont(QFont("Arial", 30, 50, False))
        select_button.clicked.connect(self._select)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(build_button)
        main_layout.addWidget(select_button)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _select(self):
        from ui.selection_window import SelectionWindow
        self.selection_window = SelectionWindow()
        self.selection_window.showMaximized()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StartWindow()
    window.showMaximized()
    app.exec_()