from matplotlib import pyplot as plt
from fuzzy.bounded_function import BoundedFunction


class FuzzyVariable:
    def __init__(self, name : str, x_min : float, x_max : float, clasifications : dict[str, BoundedFunction]):
        self.name = name
        self.x_min = x_min
        self.x_max = x_max
        for f in clasifications.values():
            if f.x_min != x_min or f.x_max != x_max:
                raise ValueError("All functions must have the same domain")
        self.clasifications = clasifications

    def get_membership(self, value : float) -> dict[str, float]:
        if value < self.x_min or value > self.x_max:
            raise ValueError(f"value {value} must be between {self.x_min} and {self.x_max}")
        return {name : f(value) for name, f in self.clasifications.items()}
    
    def plot_membership(self):
        x_values = [self.x_min + i * (self.x_max - self.x_min) / 1000 for i in range(1001)]
        
        plt.figure(figsize=(10, 6)) # type: ignore
        
        for name, f in self.clasifications.items():
            y_values = [f(x) for x in x_values]
            plt.plot(x_values, y_values, label=name) # type: ignore
        
        plt.xlabel('x') # type: ignore
        plt.ylabel('Membership Degree') # type: ignore
        plt.title(f'Fuzzy Variable {self.name} Membership Functions') # type: ignore
        plt.legend() # type: ignore
        plt.grid(True) # type: ignore
        plt.show() # type: ignore