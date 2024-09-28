import random

class Strategy_Fsa:
    def __init__(self, probs : list[list[float]], c_state : int):
        self.n_states = len(probs)
        self.n_actions = len(probs[0])
        self.c_state = c_state
        self.probs = probs

    def choose(self) -> int:
        """
        Each action of the current state has a probability of being used, choose one.
        """
        probs = self.probs[self.c_state]
        pref = [probs[0] for _ in range(len(probs))]
        for i in range(1, len(probs)):
            pref[i] = probs[i] + pref[i-1]
        
        rnd = random.random()
        for i in range(len(probs)):
            if rnd <= pref[i]:
                return i
        return len(probs)-1

    def reward(self, state : int, action : int, how_much : int):
        """
        Modify the probs to increase the probability of some specific action in a specific state.
        """
        quitted = 0
        for i in range(self.n_actions):
            if i != action:
                quitted += (self.probs[state][i] - self.probs[state][i]) / ( how_much + 1)
                self.probs[state][i] /= (how_much + 1)
        self.probs[state][action] += quitted

    def no_reward(self, state : int, action : int, how_much : int):
        """
        Modify the probs to decrease the probability of some specific action in a specific state.
        """
        quitted = self.probs[state][action] - self.probs[state][action] / (how_much + 1)
        self.probs[state][action] /= (how_much + 1)

        quitted /= (self.n_states -1)
        for i in range(self.n_actions):
            if i != action:
                self.probs[state][i] += quitted

    def change_state(self, state : int):
        self.c_state = state