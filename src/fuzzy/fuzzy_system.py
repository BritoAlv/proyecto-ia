from typing import Callable
from fuzzy.fuzzy_variable import FuzzyVariable
from fuzzy.bounded_function import *

class FuzzySystem:
    def __init__(self, input_f : list[FuzzyVariable], output_f : list[FuzzyVariable]):
        self.input_f = input_f
        self.output_f = output_f
        self.rules : dict[str, dict[str, Callable[[dict[str, dict[str, float]]], float]]]  = {}

    def fuzzify(self, crisp_values : dict[str, float]) -> dict[str, dict[str, float]]:
        result : dict[str, dict[str, float]] = {}
        for var in self.input_f:
            if var.name not in crisp_values:
                raise ValueError(f"crisp_values must have a value for {var.name}")
            if crisp_values[var.name] < var.x_min or crisp_values[var.name] > var.x_max:
                print(crisp_values[var.name])
                raise ValueError(f"crisp_values[{var.name}] must be between {var.x_min} and {var.x_max}")
            result[var.name] = var.get_membership(crisp_values[var.name])
        return result
    
    def add_rule(self, var_name : str, classification : str, rule : Callable[[dict[str, dict[str, float]]], float]):
        if var_name not in self.rules:
            self.rules[var_name] = {}
        if classification in self.rules[var_name]:
            raise ValueError(f"Rule for {var_name} and {classification} already exists")
        self.rules[var_name][classification] = rule

    def infer(self, fuzzy_values : dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
        result : dict[str, dict[str, float] ] = {}
        for var in self.output_f:
            result[var.name] = {}
            for clasification in var.clasifications:
                if clasification not in self.rules[var.name]:
                    raise ValueError(f"Rule for {var.name} and {clasification} does not exist")
                result[var.name][clasification] = self.rules[var.name][clasification](fuzzy_values)
        return result
    
    def defuzzify(self, fuzzy_values : dict[str, dict[str, float]]) -> dict[str, float]:
        result : dict[str, float] = {}
        for var in self.output_f:
            member_slices : list[BoundedFunction] = []
            for classification in var.clasifications:
                member_slices.append(var.clasifications[classification].percent_slice(fuzzy_values[var.name][classification]))
            final_function = BoundedFunction.max_combine(member_slices)
            result[var.name] = final_function.x_centroid()
        return result
    
    def process(self, crisp_values : dict[str, float]) -> dict[str, float]:
        fuzzy_values = self.fuzzify(crisp_values)
        infered_values = self.infer(fuzzy_values)
        return self.defuzzify(infered_values)