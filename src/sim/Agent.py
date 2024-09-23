from environment import Environment


from abc import ABC, abstractmethod


class Agent(ABC):
    def __init__(self, id, environment : Environment):
        self.id = id
        self.environment = environment
        self.sleep_time = 2

    @abstractmethod
    def act(self) -> None:
        pass