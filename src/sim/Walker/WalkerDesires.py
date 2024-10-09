import random

class WalkerDesires:
    def update_desires(self, walker):
        """
        Desires is a dict which contain a list of places and the desire to go to that place.
        The desire is a int >= 1.
        
        Option 1: there is a walker in my position that also wants to go to that place.
        Option 2: I know the location of the place.
        Option 3: Randomly I want to go to that place.
        Option 4: If I'm in a Place after some time I should not want to go to this place, so I decrease the desire.
        Option 5: If there are three places with the same priority make one very important and ignore others.
        """
        options = [
            self.update_desires_neigbours, 
            self.update_desires_known_places, 
            self.update_desires_random, 
            self.update_desires_reset,
            self.update_desires_max,
        ]
        random.shuffle(options)
        for rule in options:
            rule(walker)
    
    def update_desires_max(self, walker):
        max_desire = max(walker.place_desires.values())
        candidates = [place for place, desire in walker.place_desires.items() if desire == max_desire]
        if len(candidates) >= 2:
            choice = random.randint(0, len(candidates)-1)
            for i, place in enumerate(candidates):
                if i != choice:
                    walker.place_desires[place] = 1

    def update_desires_neigbours(self, walker):
        i, j = walker.position
        for walker_id in walker.environment.matrix[i][j].walkers_id:
            if walker_id != walker.id and random.random() <= walker.social_prob:
                other_walker = walker.environment.walkers[walker_id]
                for place_name in other_walker.place_desires:
                    if place_name in walker.place_desires and walker.place_beliefs[place_name].belief_state == 1:
                        walker.place_desires[place_name] += 2

    def update_desires_known_places(self, walker):
        for place_name in walker.place_desires:
            if walker.place_beliefs[place_name].belief_state == 1:
                walker.place_desires[place_name] += 2

    def update_desires_reset(self, walker):
        if random.random() <= walker.reset_prob:
            for place_name in walker.place_desires:
                walker.place_desires[place_name] = 1

    def update_desires_random(self, walker):
        choice = random.choice(list(walker.place_desires.keys()))
        walker.place_desires[choice] += 2