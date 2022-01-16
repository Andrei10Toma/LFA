from typing import Dict, List, Set
from dfa import Dfa

class Nfa:
    initial_state: int
    final_state: int
    epsilon_closure: Dict[int, Set[int]]
    alphabet: Set[str]
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
        self.alphabet = set()
        self._number_of_states = 0

    def compute_epsilon_enclosures(self):
        bfs_queue = []
        visited: Set[int] = set()
        for i in range(0, Nfa.number_of_states):
            visited.clear()
            self.epsilon_closure[i] = set()
            bfs_queue.append(i)
            self.epsilon_closure[i].add(i)
            visited.add(i)
            while len(bfs_queue) != 0:
                extracted: int = bfs_queue.pop(0)
                for transition in self.delta:
                    if transition[0] == extracted and transition[1] == None and transition[2] not in visited:
                        visited.add(transition[2])
                        bfs_queue.append(transition[2])
                        self.epsilon_closure[i].add(transition[2])
    
    def compute_dfa(self) -> Dfa:
        dfa: Dfa = Dfa([])
        number_of_states_dfa: int = 0
        bfs_queue: List[Set[int]] = []
        bfs_queue.append(frozenset(self.epsilon_closure[self.initial_state]))
        dfa.map_from_set_states_to_normal_state[frozenset(self.epsilon_closure[self.initial_state])] = number_of_states_dfa
        number_of_states_dfa += 1
        dfa._initial_state = frozenset(self.epsilon_closure[self.initial_state])
        dfa._alphabet = self.alphabet
        # compute the dfa states and tranzitions
        while len(bfs_queue) != 0:
            extracted: frozenset[int] = bfs_queue.pop(0)
            # for every character in alphabet
            for character in self.alphabet:
                new_state_set: Set[int] = set()
                for state in extracted:
                    for tranzition in self.delta:
                        if tranzition[0] == state and tranzition[1] == character:
                            new_state_set = new_state_set.union(self.epsilon_closure[tranzition[2]])
                if len(new_state_set) != 0:
                    new_state_frozenset = frozenset(new_state_set)
                    if new_state_frozenset not in dfa.map_from_set_states_to_normal_state:
                        dfa.map_from_set_states_to_normal_state[new_state_frozenset] = number_of_states_dfa
                        number_of_states_dfa += 1
                        bfs_queue.append(new_state_frozenset)
                    dfa._delta[(extracted, character)] = new_state_frozenset

        # compute the final states
        for set_states in dfa.map_from_set_states_to_normal_state.keys():
            if self.final_state in set_states:
                dfa._final_states.add(set_states)
        
        # compute the synk state
        dummy_set_state: Set[int] = set()
        dummy_set_state.add(Nfa.number_of_states)
        dummy_frozen_set_state = frozenset(dummy_set_state)
        dfa.map_from_set_states_to_normal_state[dummy_frozen_set_state] = number_of_states_dfa
        for set_states in dfa.map_from_set_states_to_normal_state.keys():
            for character in dfa._alphabet:
                if (set_states, character) not in dfa._delta:
                    dfa._delta[(set_states, character)] = dummy_frozen_set_state

        return dfa, number_of_states_dfa + 1

    def __str__(self) -> str:
        return str(self.initial_state) + ' ' + str(self.final_state) + '\n' + str(Nfa.number_of_states) + str(self.delta) + '\n' + str(self.epsilon_closure) + '\n' + str(self.alphabet)
