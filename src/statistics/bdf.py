import numpy as np
import pandas as pd
import json

def generate_random_data(n_samples, r):
    df = pd.DataFrame({
        "cars_semaphore_delay": [round(float(np.random.normal(r[0][0], r[0][1], 1)[0]), 2) for _ in range(n_samples)],
        "cars_delay": [round(float(np.random.normal(r[1][0], r[1][1], 1)[0]), 2) for _ in range(n_samples)],
        "walker_semaphore_delay": [(round(float(np.random.normal(r[2][0], r[2][1], 1)[0]), 2)) for _ in range(n_samples)],
        "walkers_delay": [round(float(np.random.normal(r[3][0], r[3][1], 1)[0]), 2) for _ in range(n_samples)]
    })
    return df
 
# Generate the DataFrame
data = generate_random_data(400, [[3, 1], [30, 7], [2, 1], [20, 5]])
data_with = generate_random_data(400, [[2, 1], [25, 4], [2, 0.4], [15, 4]])

# Save the DataFrame as a JSON file
data.to_csv('traffic_simulation_data.csv')
data.to_csv('traffic_simulation_data_whith.csv')