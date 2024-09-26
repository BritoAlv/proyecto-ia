from fuzzy.fuzzy_variable import *
from fuzzy.bounded_function import *
from fuzzy.fuzzy_system import * 

time_classification = {
    "dawn" : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0 , 180, 1),
            BoundedFunction.linear_interpolate(180, 1, 420, 0),
            BoundedFunction.linear_interpolate(420, 0, 1440, 0)
        ]
    ),
    "morning" : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 360, 0),
            BoundedFunction.linear_interpolate(360, 0, 600, 1),
            BoundedFunction.linear_interpolate(600, 1, 780, 0),
            BoundedFunction.linear_interpolate(780, 0, 1440, 0)
        ]
    ),
    "afternoon" : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 720, 0),
            BoundedFunction.linear_interpolate(720, 0, 960, 1),
            BoundedFunction.linear_interpolate(960, 1, 1200, 0),
            BoundedFunction.linear_interpolate(1200, 0, 1440, 0),

        ]
    ),
    "noon": BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0.2, 60, 0),
            BoundedFunction.linear_interpolate(60, 0, 1140, 0),
            BoundedFunction.linear_interpolate(1140, 0, 1320, 1),
            BoundedFunction.linear_interpolate(1320, 1, 1440, 0.2),
        ]
    )
}
TIME_CLASSIFICATION = "Time Classification"
time_var = FuzzyVariable( TIME_CLASSIFICATION, 0, 1440, time_classification)
# time_var.plot_membership()


distance_proportion_interest = {
    "very far" : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 1, 2, 0),
            BoundedFunction.linear_interpolate(2, 0, 10, 0)
        ]
    ),
    "far" : BoundedFunction.gaussian_function(1, 2, 2, 0, 10),
    "normal" : BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
    "near" : BoundedFunction.gaussian_function(1, 8, 2, 0, 10),
    "very near" : BoundedFunction.combine(
        [   
            BoundedFunction.linear_interpolate(0, 0, 8, 0),
            BoundedFunction.linear_interpolate(8, 0, 10, 1)
        ]
    )
}
DISTANCE_PROPORTION = "Distance Proportion"
distance_var = FuzzyVariable(DISTANCE_PROPORTION, 0, 10, distance_proportion_interest)
#distance_var.plot_membership()

wheather_proportion = {
    "raining" : BoundedFunction.gaussian_function(1, 0, 2, 0, 10),
    "cloud" : BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
    "sunny" : BoundedFunction.gaussian_function(1, 10, 2, 0, 10)
}
WHEATHER_PROPORTION = "Wheather Proportion"
wheather_var = FuzzyVariable(WHEATHER_PROPORTION, 0, 10, wheather_proportion)

person_proportion = {
    "low_person" : BoundedFunction.gaussian_function(1, 0, 2, 0, 10),
    "average_person" : BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
    "high_person" : BoundedFunction.gaussian_function(1, 10, 2, 0, 10)
}

PERSON_PROPORTION = "Person Proportion"
person_var = FuzzyVariable(PERSON_PROPORTION, 0, 10, person_proportion)

car_proportion = {
    "low_car" : BoundedFunction.gaussian_function(1, 0, 2, 0, 10),
    "average_car" : BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
    "high_car" : BoundedFunction.gaussian_function(1, 10, 2, 0, 10)
}

CAR_PROPORTION = "Car Proportion"
car_var = FuzzyVariable(CAR_PROPORTION, 0, 10, car_proportion)


fuzzySys = FuzzySystem([time_var, distance_var, wheather_var], [person_var, car_var])

# if its raining or dawn then low number of persons.
fuzzySys.add_rule(PERSON_PROPORTION, "low_person", lambda x : min(x[TIME_CLASSIFICATION]["dawn"], x[WHEATHER_PROPORTION]["raining"]))
# if distance is normal and not dawn then average.
fuzzySys.add_rule(PERSON_PROPORTION, "average_person", lambda x : max(1 - x[TIME_CLASSIFICATION]["dawn"], x[DISTANCE_PROPORTION]["normal"]))
# if interest place then high .
fuzzySys.add_rule(PERSON_PROPORTION, "high_person", lambda x : x[DISTANCE_PROPORTION]["very near"])

# if its dawn then low
fuzzySys.add_rule(CAR_PROPORTION, "low_car", lambda x : x[TIME_CLASSIFICATION]["dawn"])
# if its cloud and not dawn then average .
fuzzySys.add_rule(CAR_PROPORTION, "average_car", lambda x : max(1 - x[TIME_CLASSIFICATION]["dawn"], x[DISTANCE_PROPORTION]["normal"], x[WHEATHER_PROPORTION]["cloud"]))
# if interest place then high .
fuzzySys.add_rule(CAR_PROPORTION, "high_car", lambda x : x[DISTANCE_PROPORTION]["very near"])