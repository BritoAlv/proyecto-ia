from fuzzy.bounded_function import BoundedFunction
from fuzzy.fuzzy_system import FuzzySystem
from fuzzy.fuzzy_variable import FuzzyVariable


WHEATHER = "Wheather"
RAINING = "raining"
CLOUD = "cloud"
SUNNY = "sunny"

CAR_WAITING_TIME = "Car Waiting Time"
WALKER_WAITING_TIME = "Walker Waiting Time"

NORMAL = "normal"
CHARGED = "charged"
OVERCHARGED = "overcharged"


OVERLOAD = "Overload"
LOW = "Low"
AVERAGE = "average"
HIGH = "High"


car_wait_time = FuzzyVariable(CAR_WAITING_TIME, 0, 50, {
    NORMAL: BoundedFunction.gaussian_function(1, 0, 5, 0, 50), 
    CHARGED: BoundedFunction.gaussian_function(1, 20, 5, 0, 50), 
    OVERCHARGED: BoundedFunction.gaussian_function(1, 50, 5, 0, 50)})

walker_wait_time = FuzzyVariable(WALKER_WAITING_TIME, 0, 40, {
    NORMAL: BoundedFunction.gaussian_function(1, 0, 4, 0, 40), 
    CHARGED: BoundedFunction.gaussian_function(1, 15, 5, 0, 40), 
    OVERCHARGED: BoundedFunction.gaussian_function(1, 40, 4, 0, 40)}
)

DAWN = "dawn"
MORNING = "morning"
AFTERNOON = "afternoon"
NOON = "noon"

time_classification = {
    DAWN : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0 , 180, 1),
            BoundedFunction.linear_interpolate(180, 1, 420, 0),
            BoundedFunction.linear_interpolate(420, 0, 1440, 0)
        ]
    ),
    MORNING : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 360, 0),
            BoundedFunction.linear_interpolate(360, 0, 600, 1),
            BoundedFunction.linear_interpolate(600, 1, 780, 0),
            BoundedFunction.linear_interpolate(780, 0, 1440, 0)
        ]
    ),
    AFTERNOON : BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0, 720, 0),
            BoundedFunction.linear_interpolate(720, 0, 960, 1),
            BoundedFunction.linear_interpolate(960, 1, 1200, 0),
            BoundedFunction.linear_interpolate(1200, 0, 1440, 0),

        ]
    ),
    NOON: BoundedFunction.combine(
        [
            BoundedFunction.linear_interpolate(0, 0.2, 60, 0),
            BoundedFunction.linear_interpolate(60, 0, 1140, 0),
            BoundedFunction.linear_interpolate(1140, 0, 1320, 1),
            BoundedFunction.linear_interpolate(1320, 1, 1440, 0.2),
        ]
    )
}

TIME_CLASSIFICATION = "Time Classification" # ranges from 0 to 1440, the simulation should hold this as time.
time_var = FuzzyVariable( TIME_CLASSIFICATION, 0, 1440, time_classification)

MONTH = "Month"
month_var = FuzzyVariable(MONTH, 1, 12, {
    LOW : BoundedFunction.gaussian_function(1, 1, 2, 1, 12),
    AVERAGE : BoundedFunction.gaussian_function(1, 4, 1.5, 1, 12),
    HIGH : BoundedFunction.gaussian_function(1, 12, 2, 1, 12),      
})


CAR_PROB = "Car Prob"

wheather = FuzzyVariable(WHEATHER, 0, 1, {
    RAINING: BoundedFunction.gaussian_function(1, 0, 0.2, 0, 1), 
    CLOUD: BoundedFunction.gaussian_function(1, 0.5, 0.05, 0, 1), 
    SUNNY: BoundedFunction.gaussian_function(1, 1, 0.2, 0, 1)}
    )

car_prob = FuzzyVariable(CAR_PROB, 0, 1, {
    LOW : BoundedFunction.gaussian_function(1, 0, 0.3, 0, 1),
    AVERAGE : BoundedFunction.gaussian_function(1, 0.5, 0.01, 0, 1),
    HIGH : BoundedFunction.gaussian_function(1, 1, 0.3, 0, 1),
})

overload = FuzzyVariable(
    OVERLOAD,
    0,
    10,
    {
        LOW: BoundedFunction.gaussian_function(1, 0, 2, 0, 10),
        AVERAGE: BoundedFunction.gaussian_function(1, 5, 1.5, 0, 10),
        HIGH: BoundedFunction.gaussian_function(1, 10, 2, 0, 10),
    },
)

def build_fuzzySys():
    fuzzySys = FuzzySystem(input_f=[time_var, wheather, car_wait_time, walker_wait_time, month_var], output_f=[car_prob, overload])

    fuzzySys.add_rule(CAR_PROB, LOW, lambda x: max( min(x[TIME_CLASSIFICATION][AFTERNOON], x[TIME_CLASSIFICATION][MORNING], 1 - x[MONTH][HIGH]), max(x[CAR_WAITING_TIME][NORMAL], x[WALKER_WAITING_TIME][OVERCHARGED])))
    fuzzySys.add_rule(CAR_PROB, AVERAGE, lambda x: min( x[MONTH][AVERAGE] , x[CAR_WAITING_TIME][CHARGED], x[WALKER_WAITING_TIME][CHARGED], 1 - x[WHEATHER][CLOUD], x[TIME_CLASSIFICATION][MORNING]))
    fuzzySys.add_rule(CAR_PROB, HIGH, lambda x: max( x[MONTH][LOW], x[MONTH][HIGH], x[CAR_WAITING_TIME][OVERCHARGED], x[WALKER_WAITING_TIME][NORMAL], x[WHEATHER][RAINING], x[TIME_CLASSIFICATION][NOON], x[TIME_CLASSIFICATION][DAWN]))

    fuzzySys.add_rule(OVERLOAD, LOW, lambda x: max(x[CAR_WAITING_TIME][NORMAL], x[WALKER_WAITING_TIME][NORMAL]))
    fuzzySys.add_rule(OVERLOAD, AVERAGE, lambda x: max(x[CAR_WAITING_TIME][CHARGED], x[WALKER_WAITING_TIME][CHARGED]))
    fuzzySys.add_rule(OVERLOAD, HIGH, lambda x: max(x[CAR_WAITING_TIME][OVERCHARGED], x[WALKER_WAITING_TIME][OVERCHARGED]))
    return fuzzySys