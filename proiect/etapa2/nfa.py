from typing import Dict, List, Set

class Nfa:
    initial_state: int
    final_state: int
    epsilon_closure: Dict[int, Set[int]]
    # delta will be a list of lists. Every list of the list will have:
    # first position -> current state
    # second position -> character read from the word
    # third position -> next state
    delta: List[List[object]]
    number_of_states: int = 0
    _number_of_states: int

    def __init__(self) -> None:
        self.initial_state = -1
        self.final_state = -1
        self.epsilon_closure = dict()
        self.delta = []
        self._number_of_states = 0

    def compute_epsilon_enclosures(self):
        pass

    def __str__(self) -> str:
        return str(self.initial_state) + ' ' + str(self.final_state) + '\n' + str(Nfa.number_of_states) + str(self.delta)
