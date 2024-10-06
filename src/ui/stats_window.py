import json
import os
import pickle
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QPushButton,
    QLabel,
)
import numpy as np

from environment import Environment


class StatsWindow(QMainWindow):
    def __init__(self, environment: Environment) -> None:
        super().__init__()

        self.setWindowTitle("Stats")
        self.setMinimumWidth(700)
        self.setMinimumHeight(700)
        self._start_window = None
        self._environment: Environment = environment

        main_layout = QVBoxLayout()
        main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        main_font = QFont("Arial", 30, 50, False)
        duration_label = QLabel(
            f"Duration: {environment.date - environment.start_date}"
        )
        total_cars_label = QLabel(
            f"Total cars: {len(environment.stats.cars_delay)}"
        )
        total_walkers_label = QLabel(
            f"Total walkers: {len(environment.stats.walkers_delay)}"
        )
        average_car_semaphore_delay_label = QLabel(
            f"Average car semaphore delay: {np.average(environment.stats.cars_semaphore_delay)}"
        )
        average_walker_semaphore_delay_label = QLabel(
            f"Average walker semaphore delay: {np.average(environment.stats.walkers_semaphore_delay)}"
        )
        average_car_delay_label = QLabel(
            f"Average car delay: {np.average(environment.stats.cars_delay)}"
        )
        average_walker_delay_label = QLabel(
            f"Average walker delay: {np.average(environment.stats.walkers_delay)}"
        )
        # average_semaphore_delay = QLabel("Average semaphore delay: ")

        duration_label.setFont(main_font)
        total_cars_label.setFont(main_font)
        total_walkers_label.setFont(main_font)
        average_car_semaphore_delay_label.setFont(main_font)
        average_walker_semaphore_delay_label.setFont(main_font)
        average_car_delay_label.setFont(main_font)
        average_walker_delay_label.setFont(main_font)

        home_button = QPushButton("Home")
        home_button.setFont(QFont("Arial", 30, 50, False))
        home_button.clicked.connect(self._home)

        export_button = QPushButton("Export stats")
        export_button.setFont(QFont("Arial", 30, 50, False))
        export_button.clicked.connect(self._export)

        main_layout.addWidget(duration_label)
        main_layout.addWidget(total_cars_label)
        main_layout.addWidget(total_walkers_label)
        main_layout.addWidget(average_car_semaphore_delay_label)
        main_layout.addWidget(average_walker_semaphore_delay_label)
        main_layout.addWidget(average_car_delay_label)
        main_layout.addWidget(average_walker_delay_label)
        main_layout.addWidget(home_button)
        main_layout.addWidget(export_button)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def _home(self):
        from ui.start_window import StartWindow

        self._start_window = StartWindow()
        self._start_window.showMaximized()
        self.close()

    def _export(self):
        if "simulation_results" not in os.listdir("./"):
            os.mkdir("./simulation_results")

        json_str = json.dumps(
            {
                "cars_delay": self._environment.stats.cars_delay,
                "cars_semaphore_delay": self._environment.stats.cars_semaphore_delay,
                "walkers_delay": self._environment.stats.walkers_delay,
                "walkers_semaphore_delay": self._environment.stats.walkers_semaphore_delay,
            }
        )

        with open(f"./simulation_results/{self._environment.name}.json", "w") as file:
            file.write(json_str)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatsWindow()
    window.showMaximized()
    app.exec_()
