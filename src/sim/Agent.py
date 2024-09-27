from environment import Environment


from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, id, environment : Environment, gui_label : int):
        self.id = id
        self.environment = environment
        self.sleep_time : int = 2
        self.gui_label : int = gui_label

    @abstractmethod
    def act(self) -> None:
        pass