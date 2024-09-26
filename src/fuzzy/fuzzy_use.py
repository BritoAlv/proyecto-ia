from fuzzy.fuzzy_global import fuzzySys, TIME_CLASSIFICATION, WHEATHER_PROPORTION, DISTANCE_PROPORTION

crisp_values = {
    TIME_CLASSIFICATION : 100, # ranges from 0 to 1440 24 hours are 1440 minutes, starts at 12:00 AM.
    WHEATHER_PROPORTION : 2.0, # ranges from 0 to 10, 0 worst case, rainy.
    DISTANCE_PROPORTION : 9.0  # ranges from 0 to 10, 0 worst case, far.
}

print(fuzzySys.process(crisp_values))
