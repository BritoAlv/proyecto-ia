class PlaceBelief:
    def __init__(self, name : str, belief_pos : tuple[int, int], required : bool, priority : int = 0 ) -> None:
        self.priority = priority
        self.required = required
        self.name = name 
        self.belief_pos = belief_pos 
        self.belief_state = 0