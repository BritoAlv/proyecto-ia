from abc import ABC, abstractmethod

class Nlp(ABC):
    @abstractmethod
    def process_place_description(self) -> str:
        pass