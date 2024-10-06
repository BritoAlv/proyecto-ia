class PlaceBelief:
    def __init__(self, name : str, belief_pos : tuple[int, int]) -> None:
        self.name = name 
        self.belief_pos = belief_pos 
        self.belief_state = 0