from typing import Callable
from random import uniform
from math import isclose, exp

import matplotlib.pyplot as plt

class BoundedFunction:
    def __init__(
        self,
        f: Callable[[float], float],
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ):
        self.f = f
        self.x_min = x_min
        self.x_max = x_max
        if x_min > x_max:
            raise ValueError(f"x_min {x_min} must be <=  than x_max {x_max}")
        
        self.y_min = y_min
        self.y_max = y_max
        
        if y_min > y_max:
            raise ValueError(f"y_min {y_min} must be <=  than y_max {y_max}")

        self.area: float = self.monte_carlo_area()

    def __call__(self, x : float):
        if x < self.x_min or x > self.x_max:
            raise ValueError(f"x = {x} is not in the domain of the function")
        return self.f(x)

    def plot(self):
        x_values = [self.x_min + i * (self.x_max - self.x_min) / 1000 for i in range(1001)]
        y_values = [self.f(x) for x in x_values]
        plt.plot(x_values, y_values) # type: ignore
        plt.xlabel('x') # type: ignore
        plt.ylabel('f(x)') # type: ignore
        plt.legend() # type: ignore
        plt.show() # type: ignore

    def monte_carlo_area(self, iterations : int =100):
        goods = 0
        for _ in range(iterations):
            x = uniform(self.x_min, self.x_max)
            y = uniform(self.y_min, self.y_max)
            if y <= self.f(x):
                goods += 1
        area = (
            goods / iterations * (self.x_max - self.x_min) * (self.y_max - self.y_min)
        )
        return area

    @staticmethod
    def linear_interpolate(x1 : float, y1 : float, x2 : float, y2 : float):
        def f(x : float):
            return y1 + (y2 - y1) / (x2 - x1) * (x - x1)
        return BoundedFunction(f, min(x1, x2), max(x1,x2), min(y1,y2), max(y1, y2))
    
    @staticmethod 
    def gaussian_function(height : float, center_pos : float, s_deviation : float, x_min : float, x_max : float):
        if x_min > x_max:
            raise ValueError(f"x_min {x_min} must be <=  than x_max {x_max}")
        def f(x : float):
            return height * exp( -(x - center_pos)**2 / (2*s_deviation**2)) 
        return BoundedFunction(f, x_min, x_max, min(f(x_min), f(x_max)), height)

    @staticmethod
    def combine(functions: list['BoundedFunction']):
        x_min = functions[0].x_min
        x_max = functions[len(functions) - 1].x_max
        for i in range(1, len(functions)):
            if not isclose(functions[i].x_min, functions[i - 1].x_max):
                raise ValueError(
                    f"{i+1} function does not start ({functions[i].x_min}) where {i} function ends ({functions[i-1].x_max})"
                )
            common_point = functions[i - 1].x_max
            if not isclose(functions[i](common_point), functions[i - 1](common_point)):
                raise ValueError(
                    f"{i+1}, {i} function share the point {common_point} but have different values {functions[i](common_point)} != {functions[i-1](common_point)} so the combined function will not be continuous."
                )

        y_min = min([f.y_min for f in functions])
        y_max = max([f.y_max for f in functions])

        def combined_function(x : float):
            for f in functions:
                if f.x_min <= x <= f.x_max:
                    return f(x)
            raise ValueError(f"x = {x} is not in the domain of the combined function")

        return BoundedFunction(combined_function, x_min, x_max, y_min, y_max)

    @staticmethod
    def max_combine(functions : list['BoundedFunction']):
        x_minss = [f.x_min for f in functions]
        x_maxs = [f.x_max for f in functions]
        if len(set(x_minss)) != 1:
            raise ValueError(f"x_mins {x_minss} must be the same")
        if len(set(x_maxs)) != 1:
            raise ValueError(f"x_maxs {x_maxs} must be the same")
        y_min = min([f.y_min for f in functions])
        y_max = max([f.y_max for f in functions])

        def combined_function(x : float):
            return max([f(x) for f in functions])

        return BoundedFunction(combined_function, functions[0].x_min, functions[1].x_max, y_min, y_max)

    def percent_slice(self, percent: float):
        if percent < 0 or percent > 1:
            raise ValueError(f"percent {percent} must be between 0 and 1")
        
        y_max = self.y_min + percent * (self.y_max - self.y_min)
        def new_function(x : float):
            return min(self.f(x), y_max)
        
        result = BoundedFunction(new_function, self.x_min, self.x_max, self.y_min, y_max)
        return result

    def x_centroid(self) -> float:
        centroid = BoundedFunction.centroid_area_between_two_functions(BoundedFunction(lambda x : 0, self.x_min, self.x_max, 0, 0), self)
        return centroid[0]
    
    def area_plot(self, additional_points : list[tuple[float, float]]):
        x_values = [self.x_min + i * (self.x_max - self.x_min) / 1000 for i in range(1001)]
        y_values = [self.f(x) for x in x_values]

        plt.figure(figsize=(10, 6)) # type: ignore
        plt.plot(x_values, y_values, label='Function') # type: ignore
        plt.fill_between(x_values, y_values, color='skyblue', alpha=0.4) # type: ignore
        plt.xlabel('x') # type: ignore
        plt.ylabel('f(x)') # type: ignore
        plt.title('Area Below the Function') # type: ignore
        plt.legend() # type: ignore
        plt.grid(True) # type: ignore

        if additional_points:
            x_points, y_points = zip(*additional_points)
            plt.scatter(x_points, y_points, color='red', zorder=5)  # type: ignore


        plt.show() # type: ignore


        
        
        


    @staticmethod
    def centroid_area_between_two_functions(bottom_f : 'BoundedFunction', upper_f : 'BoundedFunction'):

        assert isclose(bottom_f.x_min, upper_f.x_min)
        assert isclose(bottom_f.x_max, upper_f.x_max)

        area_low = bottom_f.area
        area_upper = upper_f.area

        A = area_upper - area_low

        def dif_function_lambda(x : float):
            return x * (upper_f(x) - bottom_f(x))

        dif_function = BoundedFunction(
            dif_function_lambda,
            bottom_f.x_min,
            bottom_f.x_max,
            0,
            upper_f.x_max * upper_f.y_max,
        )

        def average_function_lambda(x : float):
            return (upper_f(x) - bottom_f(x)) * (upper_f(x) + bottom_f(x))

        average_function = BoundedFunction(
            average_function_lambda, bottom_f.x_min, bottom_f.x_max, 0, upper_f.y_max**2
        )

        x_centroid = 1 / A * dif_function.area
        y_centroid = 1 / A * 1 / 2 * average_function.area

        return (x_centroid, y_centroid)