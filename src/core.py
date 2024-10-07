
from datetime import datetime, timedelta
import json
import os
import pickle
from queue import PriorityQueue
from environment import Environment
from sim.Event import Event, EventHandler, EventType

def seed_events(events_queue: PriorityQueue[Event], start_date: datetime) -> None:
    # Seed a car-event
    events_queue.put(Event(start_date + timedelta(seconds=1), EventType.CAR_EVENT))
    ### Seed a rain-event
    events_queue.put(Event(start_date + timedelta(seconds=2), EventType.RAIN_EVENT))
    # Seed a walker-event
    events_queue.put(Event(start_date + timedelta(seconds=3), EventType.WALKER_EVENT))

def simulate(
        matrix_path: str, 
        smart_semaphore: bool = True, 
        start_date: datetime = datetime(2000, 1, 1), 
        duration: timedelta = timedelta(days=0, hours=2),
        seed = seed_events
    ) -> dict[str, list[int]]:

    with open(matrix_path, "rb") as file:
        matrix = pickle.load(file)
    
    environment = Environment(
        os.path.basename(matrix_path)[:-4],
        matrix,
        start_date,
        smart_semaphore
    )
    event_handler = EventHandler(environment)
    events_queue: PriorityQueue[Event] = PriorityQueue()
    seed(events_queue, start_date)

    due_date = start_date + duration
    event = events_queue.get()

    while True:
        while event.date == environment.date:
            future_event = event_handler.handle(event)
            events_queue.put(future_event)
            event = events_queue.get()

        # Convert dictionary values to list (in three cases) to avoid dictionary overwriting while iterating
        for semaphore in list(environment.semaphores.values()):
            semaphore.act()

        for car in list(environment.cars.values()):
            car.act()

        for walker in list(environment.walkers.values()):
            walker.act()

        # Increase simulation date
        environment.increase_date()
 
        print(environment.date)
        if environment.date >= due_date:
            break

    return {
        "start_date": [start_date.year, start_date.month, start_date.day,start_date.hour],
        "end_date": [due_date.year, due_date.month, due_date.day, due_date.hour],
        "cars_delay": environment.stats.cars_delay,
        "cars_semaphore_delay": environment.stats.cars_semaphore_delay,
        "walkers_delay": environment.stats.walkers_delay,
        "walkers_semaphore_delay": environment.stats.walkers_semaphore_delay,
    }

if __name__ == '__main__':
    MATRIX_PATH = './ui/matrices/matrix.pkl'
    NAME = os.path.basename(MATRIX_PATH)[:-4]

    smart_semaphore_stats = []
    standard_semaphore_stats = []

    for i in range(1, 13):
        dates= [datetime(2000, i, 1, 10), datetime(2000, i, 15, 22)]

        for date in dates:
            smart_semaphore_stats.append(
                simulate(
                matrix_path=MATRIX_PATH, 
                smart_semaphore=True, 
                start_date=date
                )
            )
            standard_semaphore_stats.append(
                simulate(
                matrix_path=MATRIX_PATH, 
                smart_semaphore=False, 
                start_date=date
                )
            )

    if "simulation_results" not in os.listdir("./"):
            os.mkdir("./simulation_results")

    with open(f'./simulation_results/smart_{NAME}.json', 'w') as file:
        file.write(json.dumps(smart_semaphore_stats))

    with open(f'./simulation_results/standard_{NAME}.json', 'w') as file:
        file.write(json.dumps(standard_semaphore_stats))

